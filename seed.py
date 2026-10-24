import random
from datetime import datetime, timedelta, date, time
from app.database import Base, engine, SessionLocal
from app.models import Area, User, CollectionEvent
from app.security import get_password_hash  # We will create this file next!

def seed_database():
    print("Dropping existing tables...")
    Base.metadata.drop_all(bind=engine)
    
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # 1. Create an Area
        area = Area(name="Lakeside", ward="Ward 4", landmark="Near the lake park")
        db.add(area)
        db.commit()
        db.refresh(area)
        print(f"Created Area: {area.name}")

        # 2. Create Users
        # Note: get_password_hash will be defined in app/security.py
        admin = User(
            name="Admin User",
            email="admin@example.com",
            password_hash=get_password_hash("admin123"),
            role="admin",
            area_id=area.id
        )
        resident = User(
            name="John Doe",
            email="john@example.com",
            password_hash=get_password_hash("password123"),
            role="resident",
            area_id=area.id
        )
        db.add_all([admin, resident])
        db.commit()
        print("Created Users: admin@example.com / john@example.com")

        # 3. Generate Historical Data (Collection Events)
        # We need data for the last 20 Mondays to test the prediction later.
        print("Generating historical collection events...")
        events = []
        today = date.today()
        
        # Find the most recent Monday
        days_since_monday = today.weekday()
        last_monday = today - timedelta(days=days_since_monday)

        for i in range(20):
            # Calculate the date for each Monday
            collection_date = last_monday - timedelta(weeks=i)
            
            # Simulate actual arrival time (around 8:30 AM to 9:00 AM)
            base_hour = 8
            base_minute = random.randint(25, 50)
            actual_time_obj = time(hour=base_hour, minute=base_minute)
            
            # Create the event
            event = CollectionEvent(
                area_id=area.id,
                collection_date=collection_date,
                expected_time=time(hour=8, minute=30), # Scheduled time
                actual_time=actual_time_obj,           # What actually happened
                status="completed"
            )
            events.append(event)
            
        db.add_all(events)
        db.commit()
        print(f"Generated {len(events)} historical collection events.")

    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()