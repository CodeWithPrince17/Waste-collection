from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from fastapi import status

from datetime import date, timedelta
from app.database import get_db
from app.auth import get_current_user
from app.models import User, Area , CollectionEvent, CollectionReport

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/resident", response_class=HTMLResponse)
def resident_dashboard(
    request: Request, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role == "admin":
        return RedirectResponse(url="/admin", status_code=status.HTTP_303_SEE_OTHER)

    areas = db.query(Area).all()

    # --- NEW LOGIC: Find yesterday's event ---
    yesterday = date.today() - timedelta(days=1)
    
    # We look for an event yesterday that hasn't been reported by this specific user yet
    yesterday_event = db.query(CollectionEvent).filter(
        CollectionEvent.area_id == current_user.area_id,
        CollectionEvent.collection_date == yesterday
    ).first()

    # Check if the user already submitted a report for it
    already_reported = False
    if yesterday_event:
        existing_report = db.query(CollectionReport).filter(
            CollectionReport.user_id == current_user.id,
            CollectionReport.collection_event_id == yesterday_event.id
        ).first()
        if existing_report:
            already_reported = True

    return templates.TemplateResponse(
        request=request, 
        name="resident.html", 
        context={
            "user": current_user, 
            "areas": areas,
            "yesterday_event": yesterday_event,
            "already_reported": already_reported
        }
    )

@router.post("/resident/set-area")
def set_resident_area(
    request: Request,
    area_id: int = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Updates the user's area based on the form submission."""
    
    # Security: Check if the area actually exists in the database
    area = db.query(Area).filter(Area.id == area_id).first()
    if not area:
        return RedirectResponse(url="/resident", status_code=status.HTTP_303_SEE_OTHER)

    # Update the user's area
    current_user.area_id = area.id
    db.commit()

    # Redirect back to the dashboard
    return RedirectResponse(url="/resident", status_code=status.HTTP_303_SEE_OTHER)