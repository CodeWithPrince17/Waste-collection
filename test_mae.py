from app.database import SessionLocal
from app.models import Prediction, CollectionEvent, Area
from datetime import date, time

db = SessionLocal()
area = db.query(Area).first()

# 1. Create a fake Prediction for a past Monday
pred_date = date(2026, 10, 19) # Use a Monday from your seed data
p = Prediction(
    area_id=area.id,
    prediction_date=pred_date,
    predicted_time=time(8, 30),
    lower_bound=time(8, 15),
    upper_bound=time(8, 45),
    confidence="High"
)
db.add(p)

# 2. Create the actual event for that same Monday (Arrived at 8:36 AM)
e = CollectionEvent(
    area_id=area.id,
    collection_date=pred_date,
    actual_time=time(8, 36)
)
db.add(e)
db.commit()

print("Test data added! MAE should be exactly 6 minutes.")
db.close()