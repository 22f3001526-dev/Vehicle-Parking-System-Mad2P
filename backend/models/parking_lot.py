"""
Parking Lot Model - Represents physical parking locations
Each lot can have multiple parking spots

Student: MAD-II Project
"""

from models import db
from datetime import datetime

class ParkingLot(db.Model):
    """
    Stores information about parking lot locations
    Admin can create, update, and delete parking lots
    """
    __tablename__ = 'parking_lots'
    
    # Basic identification
    id = db.Column(db.Integer, primary_key=True)
    prime_location_name = db.Column(db.String(200), nullable=False)
    
    # Pricing information (per hour)
    price_per_hour = db.Column(db.Float, nullable=False)
    
    # Location details
    address = db.Column(db.Text, nullable=False)
    pin_code = db.Column(db.String(10), nullable=False)
    
    # Capacity information
    number_of_spots = db.Column(db.Integer, nullable=False)
    
    # Tracking timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship: One lot has many spots
    spots = db.relationship('ParkingSpot', backref='lot', lazy='dynamic', 
                           cascade='all, delete-orphan')
    
    def get_available_spots_count(self):
        """
        Counts how many spots are currently free
        
        Returns:
            Number of available parking spots
        """
        return self.spots.filter_by(status='available').count()
    
    def get_occupied_spots_count(self):
        """
        Counts how many spots are currently occupied
        
        Returns:
            Number of occupied parking spots
        """
        return self.spots.filter_by(status='occupied').count()
    
    def can_delete(self):
        """
        Checks if this lot can be safely deleted
        We can only delete if all spots are empty
        
        Returns:
            True if safe to delete, False if spots are occupied
        """
        return self.get_occupied_spots_count() == 0
    
    def to_dict(self, include_spots_details=False):
        """
        Converts lot to dictionary for API responses
        
        Args:
            include_spots_details: Whether to include full spot information
            
        Returns:
            Dictionary with lot data
        """
        lot_data = {
            'id': self.id,
            'prime_location_name': self.prime_location_name,
            'price_per_hour': self.price_per_hour,
            'address': self.address,
            'pin_code': self.pin_code,
            'number_of_spots': self.number_of_spots,
            'available_spots': self.get_available_spots_count(),
            'occupied_spots': self.get_occupied_spots_count(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        # Include detailed spot information if requested
        if include_spots_details:
            lot_data['spots'] = [spot.to_dict() for spot in self.spots]
        
        return lot_data
    
    def __repr__(self):
        """String representation for debugging"""
        return f'<ParkingLot {self.prime_location_name} - {self.number_of_spots} spots>'
