"""
Admin routes
Handles admin-specific operations: lot/spot management, user listing, analytics
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from models import db
from models.user import User
from models.parking_lot import ParkingLot
from models.parking_spot import ParkingSpot
from models.reservation import Reservation
from utils.auth_utils import admin_required
from utils.cache import invalidate_cache
from datetime import datetime, timedelta
from sqlalchemy import func

admin_bp = Blueprint('admin', __name__)

# ============================================================================
# PARKING LOT MANAGEMENT
# ============================================================================

@admin_bp.route('/lots', methods=['GET'])
@jwt_required()
@admin_required()
def get_all_lots():
    """Get all parking lots"""
    lots = ParkingLot.query.all()
    return jsonify({
        'lots': [lot.to_dict() for lot in lots],
        'total': len(lots)
    }), 200

@admin_bp.route('/lots', methods=['POST'])
@jwt_required()
@admin_required()
def create_lot():
    """Create a new parking lot and auto-generate spots"""
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['prime_location_name', 'price_per_hour', 'address', 'pin_code', 'number_of_spots']
    if not data or not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Validate number_of_spots
    try:
        number_of_spots = int(data['number_of_spots'])
        if number_of_spots <= 0:
            return jsonify({'error': 'Number of spots must be positive'}), 400
    except ValueError:
        return jsonify({'error': 'Invalid number of spots'}), 400
    
    # Create parking lot
    lot = ParkingLot(
        prime_location_name=data['prime_location_name'],
        price_per_hour=float(data['price_per_hour']),
        address=data['address'],
        pin_code=data['pin_code'],
        number_of_spots=number_of_spots
    )
    
    try:
        db.session.add(lot)
        db.session.flush()  # Get lot.id without committing
        
        # Auto-create parking spots
        for spot_num in range(1, number_of_spots + 1):
            spot = ParkingSpot(
                lot_id=lot.id,
                spot_number=spot_num,
                status='available'
            )
            db.session.add(spot)
        
        db.session.commit()
        
        # Invalidate cache
        invalidate_cache('user:lots:available:*')
        invalidate_cache('admin:spots:*')
        
        return jsonify({
            'message': 'Parking lot created successfully',
            'lot': lot.to_dict(),
            'spots_created': number_of_spots
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create parking lot', 'details': str(e)}), 500

@admin_bp.route('/lots/<int:lot_id>', methods=['PUT'])
@jwt_required()
@admin_required()
def update_lot(lot_id):
    """Update parking lot details"""
    lot = ParkingLot.query.get(lot_id)
    if not lot:
        return jsonify({'error': 'Parking lot not found'}), 404
    
    data = request.get_json()
    
    try:
        # Update basic fields
        if 'prime_location_name' in data:
            lot.prime_location_name = data['prime_location_name']
        if 'price_per_hour' in data:
            lot.price_per_hour = float(data['price_per_hour'])
        if 'address' in data:
            lot.address = data['address']
        if 'pin_code' in data:
            lot.pin_code = data['pin_code']
        
        # Update number of spots (add/remove spots)
        if 'number_of_spots' in data:
            new_count = int(data['number_of_spots'])
            current_count = lot.number_of_spots
            
            if new_count < current_count:
                # Remove excess spots (only if they're available)
                spots_to_remove = lot.spots.order_by(ParkingSpot.spot_number.desc()).limit(current_count - new_count).all()
                for spot in spots_to_remove:
                    if spot.status == 'occupied':
                        return jsonify({'error': f'Cannot remove spot {spot.spot_number} - currently occupied'}), 400
                    db.session.delete(spot)
            
            elif new_count > current_count:
                # Add new spots
                for spot_num in range(current_count + 1, new_count + 1):
                    spot = ParkingSpot(
                        lot_id=lot.id,
                        spot_number=spot_num,
                        status='available'
                    )
                    db.session.add(spot)
            
            lot.number_of_spots = new_count
        
        lot.updated_at = datetime.utcnow()
        db.session.commit()
        
        # Invalidate cache
        invalidate_cache('user:lots:available:*')
        invalidate_cache('admin:spots:*')
        
        return jsonify({
            'message': 'Parking lot updated successfully',
            'lot': lot.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update parking lot', 'details': str(e)}), 500

@admin_bp.route('/lots/<int:lot_id>', methods=['DELETE'])
@jwt_required()
@admin_required()
def delete_lot(lot_id):
    """Delete parking lot (only if all spots are available)"""
    lot = ParkingLot.query.get(lot_id)
    if not lot:
        return jsonify({'error': 'Parking lot not found'}), 404
    
    # Check if lot can be deleted
    if not lot.can_delete():
        return jsonify({
            'error': 'Cannot delete parking lot',
            'reason': 'Some spots are currently occupied',
            'occupied_count': lot.get_occupied_spots_count()
        }), 400
    
    try:
        # Delete all spots (will cascade)
        db.session.delete(lot)
        db.session.commit()
        
        # Invalidate cache
        invalidate_cache('user:lots:available:*')
        invalidate_cache('admin:spots:*')
        
        return jsonify({'message': 'Parking lot deleted successfully'}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to delete parking lot', 'details': str(e)}), 500

# ============================================================================
# PARKING SPOT MANAGEMENT
# ============================================================================

@admin_bp.route('/spots', methods=['GET'])
@jwt_required()
@admin_required()
def get_all_spots():
    """Get all parking spots with optional filtering"""
    lot_id = request.args.get('lot_id', type=int)
    status = request.args.get('status')
    
    query = ParkingSpot.query
    
    if lot_id:
        query = query.filter_by(lot_id=lot_id)
    if status:
        query = query.filter_by(status=status)
    
    spots = query.all()
    
    return jsonify({
        'spots': [spot.to_dict(include_reservation=True) for spot in spots],
        'total': len(spots)
    }), 200

@admin_bp.route('/spots/<int:spot_id>', methods=['GET'])
@jwt_required()
@admin_required()
def get_spot_details(spot_id):
    """Get specific spot details including current vehicle info"""
    spot = ParkingSpot.query.get(spot_id)
    if not spot:
        return jsonify({'error': 'Parking spot not found'}), 404
    
    spot_data = spot.to_dict(include_reservation=True)
    spot_data['lot'] = spot.lot.to_dict() if spot.lot else None
    
    return jsonify({'spot': spot_data}), 200

# ============================================================================
# USER MANAGEMENT
# ============================================================================

@admin_bp.route('/users', methods=['GET'])
@jwt_required()
@admin_required()
def get_all_users():
    """Get all registered users"""
    users = User.query.filter_by(role='user').all()
    
    # Get reservation stats for each user
    users_data = []
    for user in users:
        user_dict = user.to_dict(include_email=True)
        user_dict['total_reservations'] = user.reservations.count()
        user_dict['active_reservations'] = user.reservations.filter_by(status='active').count()
        user_dict['completed_reservations'] = user.reservations.filter_by(status='completed').count()
        users_data.append(user_dict)
    
    return jsonify({
        'users': users_data,
        'total': len(users_data)
    }), 200

# ============================================================================
# RESERVATION MANAGEMENT
# ============================================================================

@admin_bp.route('/reservations', methods=['GET'])
@jwt_required()
@admin_required()
def get_all_reservations():
    """Get all reservations with optional filtering"""
    status = request.args.get('status')
    user_id = request.args.get('user_id', type=int)
    lot_id = request.args.get('lot_id', type=int)
    
    query = Reservation.query
    
    if status:
        query = query.filter_by(status=status)
    if user_id:
        query = query.filter_by(user_id=user_id)
    if lot_id:
        query = query.join(ParkingSpot).filter(ParkingSpot.lot_id == lot_id)
    
    reservations = query.order_by(Reservation.reserved_at.desc()).all()
    
    return jsonify({
        'reservations': [res.to_dict(include_details=True) for res in reservations],
        'total': len(reservations)
    }), 200

# ============================================================================
# ANALYTICS
# ============================================================================

@admin_bp.route('/analytics/revenue', methods=['GET'])
@jwt_required()
@admin_required()
def get_revenue_analytics():
    """Get revenue analytics"""
    # Get completed reservations with costs
    completed_reservations = Reservation.query.filter_by(status='completed').all()
    
    total_revenue = sum(res.parking_cost for res in completed_reservations if res.parking_cost)
    
    # Revenue by lot
    revenue_by_lot = db.session.query(
        ParkingLot.prime_location_name,
        func.sum(Reservation.parking_cost).label('revenue')
    ).join(ParkingSpot).join(Reservation).filter(
        Reservation.status == 'completed',
        Reservation.parking_cost.isnot(None)
    ).group_by(ParkingLot.id).all()
    
    return jsonify({
        'total_revenue': total_revenue,
        'total_completed_reservations': len(completed_reservations),
        'revenue_by_lot': [
            {'lot_name': name, 'revenue': float(revenue)} 
            for name, revenue in revenue_by_lot
        ]
    }), 200

@admin_bp.route('/analytics/occupancy', methods=['GET'])
@jwt_required()
@admin_required()
def get_occupancy_analytics():
    """Get occupancy statistics"""
    lots = ParkingLot.query.all()
    
    occupancy_data = []
    for lot in lots:
        total_spots = lot.number_of_spots
        occupied = lot.get_occupied_spots_count()
        available = lot.get_available_spots_count()
        occupancy_rate = (occupied / total_spots * 100) if total_spots > 0 else 0
        
        occupancy_data.append({
            'lot_id': lot.id,
            'lot_name': lot.prime_location_name,
            'total_spots': total_spots,
            'occupied_spots': occupied,
            'available_spots': available,
            'occupancy_rate': round(occupancy_rate, 2)
        })
    
    return jsonify({'occupancy_data': occupancy_data}), 200

@admin_bp.route('/analytics/popular-lots', methods=['GET'])
@jwt_required()
@admin_required()
def get_popular_lots():
    """Get most popular parking lots by reservation count"""
    popular_lots = db.session.query(
        ParkingLot.prime_location_name,
        func.count(Reservation.id).label('reservation_count')
    ).join(ParkingSpot).join(Reservation).group_by(
        ParkingLot.id
    ).order_by(func.count(Reservation.id).desc()).limit(10).all()
    
    return jsonify({
        'popular_lots': [
            {'lot_name': name, 'reservation_count': count}
            for name, count in popular_lots
        ]
    }), 200
