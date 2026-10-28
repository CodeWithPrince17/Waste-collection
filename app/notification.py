from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.auth import get_current_user
from app.models import User
from sqlalchemy.orm import Session
from app.database import get_db

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/resident/notifications", response_class=HTMLResponse)
def view_notifications(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    notifications = db.query(Notification).filter(
        Notification.user_id == current_user.id
    ).order_by(Notification.sent_at.desc()).all()

    return templates.TemplateResponse(
        request=request, 
        name="notifications.html", 
        context={"user": current_user, "notifications": notifications}
    )



from datetime import date, timedelta, datetime
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Area, User, CollectionEvent, Prediction, Notification
from app.prediction import calculate_prediction

def generate_daily_notifications():
    """
    This function is called by the background scheduler.
    It predicts tomorrow's collection for every area and creates notifications.
    """
    db: Session = SessionLocal()
    try:
        tomorrow = date.today() + timedelta(days=1)
        print(f"[{datetime.now()}] Running daily notification job for {tomorrow}...")

        areas = db.query(Area).all()
        for area in areas:
            # 1. Get historical data for this area on tomorrow's day of the week
            day_of_week = tomorrow.weekday()
            events = db.query(CollectionEvent).filter(
                CollectionEvent.area_id == area.id
            ).all()
            
            matching_events = [e for e in events if e.collection_date.weekday() == day_of_week]
            
            if not matching_events:
                continue # No data for this day, skip

            # 2. Run prediction
            result = calculate_prediction(matching_events)
            
            if not result["predicted_time"]:
                continue

            # 3. Save Prediction to database
            prediction = db.query(Prediction).filter(
                Prediction.area_id == area.id,
                Prediction.prediction_date == tomorrow
            ).first()

            if not prediction:
                prediction = Prediction(
                    area_id=area.id,
                    prediction_date=tomorrow,
                    predicted_time=result["predicted_time"],
                    lower_bound=result["lower_bound"],
                    upper_bound=result["upper_bound"],
                    confidence=result["confidence"]
                )
                db.add(prediction)
                db.commit()
                db.refresh(prediction)

            # 4. Create Notifications for all users in this area
            users = db.query(User).filter(User.area_id == area.id).all()
            for user in users:
                # Check if notification already exists to prevent duplicates
                existing_notif = db.query(Notification).filter(
                    Notification.user_id == user.id,
                    Notification.prediction_id == prediction.id
                ).first()

                if not existing_notif:
                    msg = (f"Waste collection expected tomorrow ({tomorrow}) "
                           f"between {result['lower_bound'].strftime('%I:%M %p')} and "
                           f"{result['upper_bound'].strftime('%I:%M %p')}.")
                    
                    new_notif = Notification(
                        user_id=user.id,
                        prediction_id=prediction.id,
                        message=msg,
                        notification_type="in_app",
                        status="sent"
                    )
                    db.add(new_notif)
            
            db.commit()
            print(f"Processed area: {area.name}")
            
    except Exception as e:
        print(f"Error in notification job: {e}")
        db.rollback()
    finally:
        db.close()