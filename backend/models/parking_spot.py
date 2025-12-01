"""
Parking Spot Model - Individual parking spaces within a lot
Tracks whether each spot is available or occupied

MAD-II Student Project
"""

from models import db
from datetime import datetime

class ParkingSpot(db.Model):
    """
    Represents a single parking space in a parking lot
    Each spot can be either 'available' or 'occupied'
    """
    __tablename__ = 'parking_spots'
    
    # Identification
    id = db.Column(db.Integer, primary_key=True)
    lot_id = db.Column(db.Integer, db.ForeignKey('parking_lots.id'), nullable=False, index=True)
    spot_number = db.Column(db.Integer, nullable=False)  # Spot number within the lot (1, 2, 3...)
    
    # Current status of the spot
    status = db.Column(db.String(20), nullable=False, default='available')
    
    # When this spot was created
    created_at = db.Column(db.Integer, default=datetime.utcnow)
    
    # Relationship: One spot can have many reservations over time
    reservations = db.relationship('Reservation', backref='spot', lazy='dynamic', 
                                   cascade='all, delete-orphan')
    
    def get_current_reservation(self):
        """
        Finds if there's an active reservation for this spot right now
        
        Returns:
            Reservation object if spot is currently reserved, None otherwise
        """
        return self.reservations.filter_by(status='active').first()
    
    def is_available(self):
        """
        Simple check if spot is free to use
        
        Returns:
            True if available, False if occupied
        """
        return self.status == 'available'
    
    def mark_occupied(self):
        """Updates spot status when someone parks here"""
        self.status = 'occupied'
    
    def mark_available(self):
        """Updates spot status when someone leaves"""
        self.status = 'available'
    
    def to_dict(self, include_reservation_info=False):
        """
        Converts spot to dictionary for API responses
        
        Args:
            include_reservation_info: Whether to include current reservation details
            
        Returns:
            Dictionary with spot data
        """
        spot_data = {
            'id': self.id,
            'lot_id': self.lot_id,
            'spot_number': self.spot_number,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        
        # Add current reservation info if requested
        if include_reservation_info:
            current_res = self.get_current_reservation()
            if current_res:
                spot_data['current_reservation'] = current_res.to_dict()
        
        return spot_data
    
    def __repr__(self):
        """String representation for debugging"""
        return f'<ParkingSpot #{self.spot_number} in Lot {self.lot_id} - {self.status}>'
