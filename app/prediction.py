from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import date, time, timedelta
from typing import Optional
import statistics

from app.database import get_db
from app.auth import get_current_user
from app.models import User, Area, CollectionEvent, Prediction

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# ==========================================
# THE CORE ALGORITHM (Pure Function)
# ==========================================
def calculate_prediction(events: list[CollectionEvent]) -> dict:
    """
    Takes a list of historical collection events and calculates 
    the expected time, window, and confidence.
    """
    # 1. Filter out any events that don't have an actual time recorded
    valid_events = [e for e in events if e.actual_time is not None]
    
    if not valid_events:
        return {
            "predicted_time": None,
            "lower_bound": None,
            "upper_bound": None,
            "confidence": "Insufficient Data"
        }

    # 2. Convert times to total minutes from midnight (e.g., 08:30 = 510)
    minutes_list = []
    for e in valid_events:
        mins = (e.actual_time.hour * 60) + e.actual_time.minute
        minutes_list.append(mins)

    # 3. Calculate Average
    avg_minutes = statistics.mean(minutes_list)

    # 4. Calculate Variance (Standard Deviation)
    # If we have 1 record, variance is 0. Let's use a default variance of 15 mins.
    if len(minutes_list) > 1:
        std_dev = statistics.stdev(minutes_list)
    else:
        std_dev = 15 

    # 5. Calculate Time Window (± 1.5 Standard Deviations)
    window_buffer = std_dev * 1.5
    lower_mins = max(0, int(avg_minutes - window_buffer))
    upper_mins = min(1439, int(avg_minutes + window_buffer))

    # 6. Determine Confidence
    count = len(valid_events)
    if count < 3:
        confidence = "Insufficient Data"
    elif count < 6:
        confidence = "Low"
    elif count < 10:
        confidence = "Moderate"
    else:
        confidence = "High"

    # 7. Convert back to Python time objects
    def mins_to_time(m):
        return time(hour=m // 60, minute=m % 60)

    return {
        "predicted_time": mins_to_time(int(avg_minutes)),
        "lower_bound": mins_to_time(lower_mins),
        "upper_bound": mins_to_time(upper_mins),
        "confidence": confidence,
        "count": count
    }

# ==========================================
# THE ROUTES (HTTP Layer)
# ==========================================

@router.get("/resident/prediction", response_class=HTMLResponse)
def view_prediction(
    request: Request,
    target_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user.area_id:
        return RedirectResponse(url="/resident", status_code=303)
        
    if not target_date:
        target_date = date.today()

    # Fetch ALL historical events for this user's area
    events = db.query(CollectionEvent).filter(
        CollectionEvent.area_id == current_user.area_id
    ).all()

    # Filter events by the same day of the week (e.g., Monday == Monday)
    day_of_week = target_date.weekday() # 0 = Monday, 6 = Sunday
    matching_events = [e for e in events if e.collection_date.weekday() == day_of_week]

    # Run the algorithm
    result = calculate_prediction(matching_events)

    return templates.TemplateResponse(
        request=request,
        name="prediction.html",
        context={
            "user": current_user,
            "target_date": target_date,
            "result": result
        }
    )