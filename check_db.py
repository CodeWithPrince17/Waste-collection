from app.database import SessionLocal
from app.models import User, Area, CollectionEvent

db = SessionLocal()

print("--- USERS ---")
users = db.query(User).all()
for u in users:
    print(f"Name: {u.name}, Email: {u.email}, Role: {u.role}, Area: {u.area.name}")

print("\n--- COLLECTION EVENTS (First 3) ---")
events = db.query(CollectionEvent).limit(3).all()
for e in events:
    print(f"Date: {e.collection_date}, Expected: {e.expected_time}, Actual: {e.actual_time}")

db.close()