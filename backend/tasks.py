"""
Background Tasks
This file contains all the long-running jobs that run in the background.
We use Celery to run these so they don't slow down the website.

Tasks included:
1. Daily Reminders - Reminds users to book a spot
2. Monthly Report - Sends activity summary to admin
3. CSV Export - Exports user history to a file

Student Project - MAD-II
"""

from celery_worker import celery
from models import db
from models.user import User
from models.reservation import Reservation
from models.parking_lot import ParkingLot
from datetime import datetime, timedelta
import csv
import io
import smtplib  # We will simulate email sending
from email.mime.text import MIMEText

# ============================================================================
# 1. DAILY REMINDER TASK
# ============================================================================

@celery.task(name='tasks.send_daily_reminders')
def send_daily_reminders():
    """
    Finds users who haven't booked in a while and sends them a reminder.
    Runs once a day.
    """
    print("\n" + "="*50)
    print("⏰ STARTING DAILY REMINDER JOB")
    print("="*50)
    
    # Find users who haven't booked in the last 7 days
    # (Or users who have never booked)
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    
    users_to_remind = User.query.filter(
        (User.last_booking_date < seven_days_ago) | (User.last_booking_date == None),
        User.role == 'user'  # Only remind regular users, not admins
    ).all()
    
    print(f"Found {len(users_to_remind)} users to remind.")
    
    for user in users_to_remind:
        # In a real app, we would send an actual email here.
        # For this project, we will simulate it by printing to the console/log.
        
        message = f"Hi {user.username}! We haven't seen you in a while. Check out available parking spots!"
        
        # Simulate sending email
        print(f"📧 SENDING EMAIL TO: {user.email}")
        print(f"   Subject: We miss you!")
        print(f"   Body: {message}")
        print("-" * 30)
        
    print("="*50)
    print("✅ DAILY REMINDERS SENT SUCCESSFULLY")
    print("="*50 + "\n")
    
    return f"Sent reminders to {len(users_to_remind)} users"


# ============================================================================
# 2. MONTHLY ACTIVITY REPORT
# ============================================================================

@celery.task(name='tasks.send_monthly_report')
def send_monthly_report():
    """
    Calculates monthly statistics and sends a report to the admin.
    Runs on the 1st of every month.
    """
    print("\n" + "="*50)
    print("📊 GENERATING MONTHLY ACTIVITY REPORT")
    print("="*50)
    
    # Calculate stats for the report
    total_users = User.query.count()
    total_reservations = Reservation.query.count()
    active_reservations = Reservation.query.filter_by(status='active').count()
    
    # Calculate total revenue
    completed_reservations = Reservation.query.filter_by(status='completed').all()
    total_revenue = sum(r.parking_cost for r in completed_reservations if r.parking_cost)
    
    # Create the report content (HTML format)
    report_html = f"""
    <h1>Monthly Parking Activity Report</h1>
    <p>Here is the summary of activity for this month:</p>
    <ul>
        <li><strong>Total Registered Users:</strong> {total_users}</li>
        <li><strong>Total Reservations Made:</strong> {total_reservations}</li>
        <li><strong>Current Active Parkings:</strong> {active_reservations}</li>
        <li><strong>Total Revenue Generated:</strong> ₹{total_revenue:.2f}</li>
    </ul>
    <p>Keep up the good work!</p>
    """
    
    # Find the admin to send the report to
    admin = User.query.filter_by(role='admin').first()
    
    if admin:
        print(f"📧 SENDING REPORT TO ADMIN: {admin.email}")
        print(f"   Subject: Monthly Activity Report")
        print(f"   Content: \n{report_html}")
    else:
        print("⚠ No admin found to send report to!")
        
    print("="*50)
    print("✅ MONTHLY REPORT GENERATED")
    print("="*50 + "\n")
    
    return "Monthly report sent"


# ============================================================================
# 3. CSV EXPORT TASK
# ============================================================================

@celery.task(name='tasks.export_user_history')
def export_user_history(user_id):
    """
    Exports a user's parking history to a CSV file.
    This is triggered by the user from the dashboard.
    """
    print("\n" + "="*50)
    print(f"📂 STARTING CSV EXPORT FOR USER ID: {user_id}")
    print("="*50)
    
    user = User.query.get(user_id)
    if not user:
        print(f"⚠ User {user_id} not found!")
        return "User not found"
        
    # Get all reservations for this user
    reservations = Reservation.query.filter_by(user_id=user_id).all()
    
    # Create a CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header row
    writer.writerow(['Reservation ID', 'Lot Name', 'Spot Number', 'Date', 'Duration', 'Cost', 'Status'])
    
    # Write data rows
    for res in reservations:
        lot_name = res.spot.lot.prime_location_name if res.spot and res.spot.lot else "Unknown"
        spot_num = res.spot.spot_number if res.spot else "N/A"
        date = res.reserved_at.strftime('%Y-%m-%d %H:%M') if res.reserved_at else "N/A"
        cost = f"₹{res.parking_cost:.2f}" if res.parking_cost else "N/A"
        
        writer.writerow([
            res.id,
            lot_name,
            spot_num,
            date,
            res.get_duration_string(),
            cost,
            res.status
        ])
        
    # In a real app, we would email this file as an attachment.
    # Here, we will simulate it.
    csv_content = output.getvalue()
    
    print(f"📧 SENDING CSV EXPORT TO: {user.email}")
    print(f"   Subject: Your Parking History Export")
    print(f"   Attachment: parking_history.csv ({len(reservations)} records)")
    print("-" * 30)
    print("CSV PREVIEW (First 3 lines):")
    print("\n".join(csv_content.split("\n")[:3]))
    print("..." + "\n")
    
    print("="*50)
    print("✅ CSV EXPORT COMPLETED")
    print("="*50 + "\n")
    
    return "Export successful"
