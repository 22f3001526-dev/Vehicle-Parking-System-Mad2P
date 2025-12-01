"""
User routes
Handles user-specific operations: lot viewing, reservations, history, analytics
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db
from models.user import User
from models.parking_lot import ParkingLot
from models.parking_spot import ParkingSpot
from models.reservation import Reservation
from utils.auth_utils import user_required, get_current_user
from utils.cache import invalidate_cache
from datetime import datetime
from sqlalchemy import func

user_bp = Blueprint('user', __name__)

# ============================================================================
# PARKING LOT VIEWING
# ============================================================================

@user_bp.route('/lots/available', methods=['GET'])
@jwt_required()
@user_required()
def get_available_lots():
    """Get all parking lots with availability information"""
    lots = ParkingLot.query.all()
    
    available_lots = []
    for lot in lots:
        if lot.get_available_spots_count() > 0:
            lot_data = lot.to_dict()
            available_lots.append(lot_data)
    
    return jsonify({
        'lots': available_lots,
        'total': len(available_lots)
    }), 200

# ============================================================================
# RESERVATION MANAGEMENT
# ============================================================================

@user_bp.route('/reserve', methods=['POST'])
@jwt_required()
@user_required()
def reserve_spot():
    """Reserve first available spot in selected lot"""
    data = request.get_json()
    user = get_current_user()
    
    if not data or 'lot_id' not in data:
        return jsonify({'error': 'Missing lot_id'}), 400
    
    lot_id = data['lot_id']
    lot = ParkingLot.query.get(lot_id)
    
    if not lot:
        return jsonify({'error': 'Parking lot not found'}), 404
    
    # Check if user already has an active reservation
    active_reservation = Reservation.query.filter_by(
        user_id=user.id,
        status='active'
    ).first()
    
    if active_reservation:
        return jsonify({
            'error': 'You already have an active reservation',
            'reservation_id': active_reservation.id
        }), 400
    
    # Find first available spot in the lot
    available_spot = ParkingSpot.query.filter_by(
        lot_id=lot_id,
        status='available'
    ).first()
    
    if not available_spot:
        return jsonify({'error': 'No available spots in this parking lot'}), 400
    
    try:
        # Create reservation
        reservation = Reservation(
            spot_id=available_spot.id,
            user_id=user.id,
            reserved_at=datetime.utcnow(),
            status='reserved'
        )
        
        db.session.add(reservation)
        db.session.commit()
        
        # Invalidate available lots cache
        invalidate_cache('user:lots:available:*')
        invalidate_cache('admin:spots:*')
        
        return jsonify({
            'message': 'Spot reserved successfully',
            'reservation': reservation.to_dict(include_details=True)
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to reserve spot', 'details': str(e)}), 500

@user_bp.route('/occupy/<int:reservation_id>', methods=['POST'])
@jwt_required()
@user_required()
def occupy_spot(reservation_id):
    """Mark spot as occupied (user has parked)"""
    user = get_current_user()
    reservation = Reservation.query.get(reservation_id)
    
    if not reservation:
        return jsonify({'error': 'Reservation not found'}), 404
    
    # Verify ownership
    if reservation.user_id != user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Check status
    if reservation.status != 'reserved':
        return jsonify({'error': 'Reservation is not in reserved state'}), 400
    
    try:
        # Update reservation
        reservation.parking_timestamp = datetime.utcnow()
        reservation.status = 'active'
        
        # Update spot status
        reservation.spot.mark_occupied()
        
        # Update user's last booking date
        user.last_booking_date = datetime.utcnow()
        
        db.session.commit()
        
        # Invalidate cache
        invalidate_cache('admin:spots:*')
        
        return jsonify({
            'message': 'Spot occupied successfully',
            'reservation': reservation.to_dict(include_details=True)
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to occupy spot', 'details': str(e)}), 500

@user_bp.route('/release/<int:reservation_id>', methods=['POST'])
@jwt_required()
@user_required()
def release_spot(reservation_id):
    """Release spot (user is leaving)"""
    user = get_current_user()
    reservation = Reservation.query.get(reservation_id)
    
    if not reservation:
        return jsonify({'error': 'Reservation not found'}), 404
    
    # Verify ownership
    if reservation.user_id != user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Check status
    if reservation.status != 'active':
        return jsonify({'error': 'Reservation is not in active state'}), 400
    
    try:
        # Update reservation
        reservation.leaving_timestamp = datetime.utcnow()
        reservation.status = 'completed'
        
        # Calculate cost
        if reservation.spot and reservation.spot.lot:
            price_per_hour = reservation.spot.lot.price_per_hour
            reservation.parking_cost = reservation.calculate_cost(price_per_hour)
        
        # Update spot status
        reservation.spot.mark_available()
        
        db.session.commit()
        
        # Invalidate cache
        invalidate_cache('user:lots:available:*')
        invalidate_cache('admin:spots:*')
        
        return jsonify({
            'message': 'Spot released successfully',
            'reservation': reservation.to_dict(include_details=True),
            'cost': reservation.parking_cost
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to release spot', 'details': str(e)}), 500

@user_bp.route('/current', methods=['GET'])
@jwt_required()
@user_required()
def get_current_reservation():
    """Get user's current active reservation"""
    user = get_current_user()
    
    active_reservation = Reservation.query.filter_by(
        user_id=user.id,
        status='active'
    ).first()
    
    if not active_reservation:
        # Also check for reserved status
        reserved_reservation = Reservation.query.filter_by(
            user_id=user.id,
            status='reserved'
        ).first()
        
        if reserved_reservation:
            return jsonify({
                'reservation': reserved_reservation.to_dict(include_details=True)
            }), 200
        
        return jsonify({'reservation': None}), 200
    
    return jsonify({
        'reservation': active_reservation.to_dict(include_details=True)
    }), 200

# ============================================================================
# RESERVATION HISTORY
# ============================================================================

@user_bp.route('/reservations', methods=['GET'])
@jwt_required()
@user_required()
def get_user_reservations():
    """Get user's reservation history"""
    user = get_current_user()
    
    # Pagination
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    # Filter by status if provided
    status = request.args.get('status')
    
    query = Reservation.query.filter_by(user_id=user.id)
    
    if status:
        query = query.filter_by(status=status)
    
    query = query.order_by(Reservation.reserved_at.desc())
    
    # Paginate
    paginated_reservations = query.paginate(page=page, per_page=per_page, error_out=False)
    
    reservations_data = [res.to_dict(include_details=True) for res in paginated_reservations.items]
    
    return jsonify({
        'reservations': reservations_data,
        'total': paginated_reservations.total,
        'page': page,
        'per_page': per_page,
        'total_pages': paginated_reservations.pages
    }), 200

# ============================================================================
# USER ANALYTICS
# ============================================================================

@user_bp.route('/analytics/spending', methods=['GET'])
@jwt_required()
@user_required()
def get_spending_analytics():
    """Get user's spending analytics"""
    user = get_current_user()
    
    # Get completed reservations
    completed_reservations = Reservation.query.filter_by(
        user_id=user.id,
        status='completed'
    ).all()
    
    total_spent = sum(res.parking_cost for res in completed_reservations if res.parking_cost)
    
    # Group by month
    monthly_spending = db.session.query(
        func.strftime('%Y-%m', Reservation.leaving_timestamp).label('month'),
        func.sum(Reservation.parking_cost).label('total')
    ).filter(
        Reservation.user_id == user.id,
        Reservation.status == 'completed',
        Reservation.parking_cost.isnot(None)
    ).group_by('month').order_by('month').all()
    
    return jsonify({
        'total_spent': total_spent,
        'total_completed_parkings': len(completed_reservations),
        'monthly_spending': [
            {'month': month, 'amount': float(total)}
            for month, total in monthly_spending
        ]
    }), 200

@user_bp.route('/analytics/usage', methods=['GET'])
@jwt_required()
@user_required()
def get_usage_analytics():
    """Get user's parking usage patterns"""
    user = get_current_user()
    
    # Most used parking lots
    most_used_lots = db.session.query(
        ParkingLot.prime_location_name,
        func.count(Reservation.id).label('usage_count')
    ).join(ParkingSpot).join(Reservation).filter(
        Reservation.user_id == user.id
    ).group_by(ParkingLot.id).order_by(
        func.count(Reservation.id).desc()
    ).limit(5).all()
    
    # Total reservations by status
    status_counts = db.session.query(
        Reservation.status,
        func.count(Reservation.id).label('count')
    ).filter(
        Reservation.user_id == user.id
    ).group_by(Reservation.status).all()
    
    return jsonify({
        'most_used_lots': [
            {'lot_name': name, 'usage_count': count}
            for name, count in most_used_lots
        ],
        'reservations_by_status': {
            status: count for status, count in status_counts
        }
    }), 200

# ============================================================================
# CSV EXPORT (Will be async with Celery in Milestone 8)
# ============================================================================

@user_bp.route('/export/csv', methods=['POST'])
@jwt_required()
@user_required()
def trigger_csv_export():
    """
    Triggers the background job to export parking history
    This returns immediately while the heavy work happens in background
    """
    user = get_current_user()
    
    # Import the task here to avoid circular imports
    from tasks import export_user_history
    
    # Start the background task
    # .delay() is how we tell Celery to run this asynchronously
    export_user_history.delay(user.id)
    
    return jsonify({
        'message': 'Export started! You will receive an email with the CSV shortly.',
        'status': 'processing'
    }), 200
