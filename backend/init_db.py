"""
Database Initialization Script
Run this file to set up the database with tables and sample data

Author: MAD-II Student Project
Usage: python init_db.py
"""

import sys
import os

# Make sure we can import from the backend folder
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from config import Config
from models import db
from models.user import User
from models.parking_lot import ParkingLot
from models.parking_spot import ParkingSpot
from models.reservation import Reservation

def create_app():
    """
    Creates a minimal Flask app just for database operations
    We don't need the full app, just enough to access the database
    """
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    return app

def init_database():
    """
    Main function to initialize the entire database
    This will:
    1. Create all tables
    2. Create admin account
    3. Create some sample users
    4. Create sample parking lots
    5. Create parking spots for each lot  
    """
    print("\n" + "="*70)
    print("🚗 VEHICLE PARKING SYSTEM - Database Setup")
    print("="*70 + "\n")
    
    app = create_app()
    
    with app.app_context():
        # Step 1: Drop existing tables if any (fresh start)
        print("Step 1: Cleaning up old database...")
        db.drop_all()
        print("  ✓ Old tables removed\n")
        
        # Step 2: Create all new tables based on our models
        print("Step 2: Creating database tables...")
        db.create_all()
        print("  ✓ Tables created: users, parking_lots, parking_spots, reservations\n")
        
        # Step 3: Create the admin account
        print("Step 3: Setting up administrator account...")
        admin_user = User(
            username='admin',
            email='admin@parkingapp.com',
            role='admin'
        )
        admin_user.set_password('admin123')  # Set admin password
        db.session.add(admin_user)
        print("  ✓ Admin account created\n")
        
        # Step 4: Create some test users for demonstration
        print("Step 4: Creating sample user accounts...")
        
        test_user1 = User(
            username='john_doe',
            email='john.doe@example.com',
            role='user'
        )
        test_user1.set_password('password123')
        db.session.add(test_user1)
        
        test_user2 = User(
            username='jane_smith',
            email='jane.smith@example.com',
            role='user'
        )
        test_user2.set_password('password123')
        db.session.add(test_user2)
        
        # Save users to database
        db.session.commit()
        print("  ✓ Created 3 user accounts (1 admin + 2 regular users)\n")
        
        # Step 5: Create sample parking lots
        print("Step 5: Adding sample parking lots...")
        
        # Lot 1: Downtown area
        downtown_lot = ParkingLot(
            prime_location_name='Downtown Business Plaza',
            price_per_hour=50.0,
            address='123 Main Street, Downtown District',
            pin_code='110001',
            number_of_spots=20
        )
        db.session.add(downtown_lot)
        
        # Lot 2: Shopping area
        mall_lot = ParkingLot(
            prime_location_name='Central Shopping Mall',
            price_per_hour=40.0,
            address='456 Mall Road, Shopping District',
            pin_code='110002',
            number_of_spots=30
        )
        db.session.add(mall_lot)
        
        # Lot 3: Airport
        airport_lot = ParkingLot(
            prime_location_name='International Airport Parking',
            price_per_hour=75.0,
            address='789 Airport Road, Terminal 2',
            pin_code='110037',
            number_of_spots=50
        )
        db.session.add(airport_lot)
        
        # Save parking lots
        db.session.commit()
        total_lots = ParkingLot.query.count()
        print(f"  ✓ Created {total_lots} parking lots\n")
        
        # Step 6: Generate parking spots for each lot
        print("Step 6: Generating parking spots...")
        
        total_spots = 0
        # Loop through each parking lot we just created
        for lot in ParkingLot.query.all():
            # Create spots numbered 1, 2, 3, ... up to number_of_spots
            for spot_number in range(1, lot.number_of_spots + 1):
                new_spot = ParkingSpot(
                    lot_id=lot.id,
                    spot_number=spot_number,
                    status='available'  # All spots start as available
                )
                db.session.add(new_spot)
                total_spots += 1
        
        # Save all parking spots
        db.session.commit()
        print(f"  ✓ Created {total_spots} parking spots across all lots\n")
        
        # All done! Show summary
        print("="*70)
        print("✅ DATABASE SETUP COMPLETE!")
        print("="*70)
        
        print("\n📍 Database Location:")
        print(f"   {app.config['SQLALCHEMY_DATABASE_URI']}")
        
        print("\n👤 Login Credentials:")
        print("\n   ADMIN ACCESS:")
        print("   Username: admin")
        print("   Password: admin123")
        
        print("\n   SAMPLE USER ACCOUNTS:")
        print("   Username: john_doe    | Password: password123")
        print("   Username: jane_smith  | Password: password123")
        
        print("\n📊 Database Summary:")
        print(f"   Total Users: {User.query.count()}")
        print(f"   Total Parking Lots: {ParkingLot.query.count()}")
        print(f"   Total Parking Spots: {ParkingSpot.query.count()}")
        
        print("\n" + "="*70)
        print("You can now run the Flask server with: python app.py")
        print("="*70 + "\n")

# Run the initialization when this file is executed
if __name__ == '__main__':
    init_database()
