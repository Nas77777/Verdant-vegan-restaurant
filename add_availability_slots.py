from datetime import datetime, timedelta
from app import app, db, Availability

def add_standard_dining_slots():
    """
    Adds standard dining reservation slots to the database.
    Each reservation lasts for 2 hours and is available for standard dining.
    """

    with app.app_context():
        # Define the date range (next 30 days)
        start_date = datetime.now().date()
        end_date = start_date + timedelta(days=80)
        
        # Define time slots (11:00 AM to 9:00 PM with 1-hour)
        time_slots = [
            (datetime.strptime('11:00', '%H:%M').time(), datetime.strptime('12:00', '%H:%M').time()),
            (datetime.strptime('12:00', '%H:%M').time(), datetime.strptime('13:00', '%H:%M').time()),
            (datetime.strptime('13:00', '%H:%M').time(), datetime.strptime('14:00', '%H:%M').time()),
            (datetime.strptime('14:00', '%H:%M').time(), datetime.strptime('15:00', '%H:%M').time()),
            (datetime.strptime('15:00', '%H:%M').time(), datetime.strptime('16:00', '%H:%M').time()),
            (datetime.strptime('16:00', '%H:%M').time(), datetime.strptime('17:00', '%H:%M').time()),
            (datetime.strptime('17:00', '%H:%M').time(), datetime.strptime('18:00', '%H:%M').time()),
            (datetime.strptime('18:00', '%H:%M').time(), datetime.strptime('19:00', '%H:%M').time()),
            (datetime.strptime('19:00', '%H:%M').time(), datetime.strptime('20:00', '%H:%M').time()),
            (datetime.strptime('20:00', '%H:%M').time(), datetime.strptime('21:00', '%H:%M').time()),
        ]
        
        slots_added = 0
        
        # Create availability slots for each day and time slot
        current_date = start_date
        while current_date <= end_date:
            for start_time, end_time in time_slots:
                # Check if slot already exists
                existing_slot = Availability.query.filter_by(
                    date=current_date,
                    start_time=start_time,
                    end_time=end_time
                ).first()
                
                if not existing_slot:
                    # Create new availability slot
                    availability = Availability(
                        date=current_date,
                        start_time=start_time,
                        end_time=end_time,
                        is_available=True,
                        reservation_type="standard_dining"
                    )
                    db.session.add(availability)
                    slots_added += 1
            
            current_date += timedelta(days=1)

        db.session.commit()
        print(f"Successfully added {slots_added} standard dining slots.")

if __name__ == "__main__":
    add_standard_dining_slots()