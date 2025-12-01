"""
Reservation Model - Tracks parking bookings and usage
Records when users park and leave, calculates costs

Student Project - MAD-II
"""

from models import db
from datetime import datetime
import math

class Reservation(db.Model):
    """
    Keeps track of parking reservations
    Handles the complete lifecycle: reserve → park → leave
    """
    __tablename__ = 'reservations'
    
    # Primary identification
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign keys linking to spot and user
    spot_id = db.Column(db.Integer, db.ForeignKey('parking_spots.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    # Important timestamps for tracking
    reserved_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    parking_timestamp = db.Column(db.DateTime, nullable=True)  # When user actually parks
    leaving_timestamp = db.Column(db.DateTime, nullable=True)  # When user leaves
    
    # Status tracking: 'reserved' → 'active' → 'completed'
    status = db.Column(db.String(20), nullable=False, default='reserved')
    
    # Cost information (calculated when leaving)
    parking_cost = db.Column(db.Float, nullable=True)
    
    # Optional notes
    remarks = db.Column(db.Text, nullable=True)
    
    def calculate_duration_hours(self):
        """
        Calculates how long the vehicle was parked
        
        Returns:
            Duration in hours (as a float)
        """
        # Can't calculate if timestamps are missing
        if not self.parking_timestamp or not self.leaving_timestamp:
            return 0
        
        # Calculate time difference
        time_diff = self.leaving_timestamp - self.parking_timestamp
        hours = time_diff.total_seconds() / 3600  # Convert seconds to hours
        
        return hours
    
    def calculate_cost(self, hourly_rate):
        """
        Calculates parking cost based on duration
        We round UP to the nearest hour for billing
        
        Args:
            hourly_rate: Price per hour for this parking lot
            
        Returns:
            Total cost in rupees
        """
        hours_parked = self.calculate_duration_hours()
        
        # Round up to nearest hour (even 10 min = 1 hour charge)
        billable_hours = math.ceil(hours_parked) if hours_parked > 0 else 0
        
        total_cost = billable_hours * hourly_rate
        return total_cost
    
    def get_duration_string(self):
        """
        Returns human-readable duration like "2h 30m"
        
        Returns:
            String representation of duration
        """
        if not self.parking_timestamp or not self.leaving_timestamp:
            return "Not yet completed"
        
        time_diff = self.leaving_timestamp - self.parking_timestamp
        hours = int(time_diff.total_seconds() // 3600)
        minutes = int((time_diff.total_seconds() % 3600) // 60)
        
        return f"{hours}h {minutes}m"
    
    def to_dict(self, include_full_details=False):
        """
        Converts reservation to dictionary for API
        
        Args:
            include_full_details: Whether to include lot and user names
            
        Returns:
            Dictionary with reservation data
        """
        res_data = {
            'id': self.id,
            'spot_id': self.spot_id,
            'user_id': self.user_id,
            'reserved_at': self.reserved_at.isoformat() if self.reserved_at else None,
            'parking_timestamp': self.parking_timestamp.isoformat() if self.parking_timestamp else None,
            'leaving_timestamp': self.leaving_timestamp.isoformat() if self.leaving_timestamp else None,
            'status': self.status,
            'parking_cost': self.parking_cost,
            'duration': self.get_duration_string(),
            'remarks': self.remarks
        }
        
        # Add extra details if requested (for detailed views)
        if include_full_details:
            # Add spot information
            if self.spot:
                res_data['spot_number'] = self.spot.spot_number
                # Add lot information
                if self.spot.lot:
                    res_data['lot_name'] = self.spot.lot.prime_location_name
                    res_data['lot_address'] = self.spot.lot.address
                    res_data['price_per_hour'] = self.spot.lot.price_per_hour
            
            # Add user information
            if self.user:
                res_data['username'] = self.user.username
        
        return res_data
    
    def __repr__(self):
        """String representation for debugging"""
        return f'<Reservation #{self.id} - User:{self.user_id} - {self.status}>'
