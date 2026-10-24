from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from fastapi import status
from datetime import date, time

from app.database import get_db
from app.auth import require_admin
from app.models import User, Area, CollectionEvent

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/admin", response_class=HTMLResponse)
def admin_dashboard(
    request: Request, 
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin) # SECURITY GUARD
):
    """Serves the admin dashboard with high-level statistics."""
    
    # Fetch stats for the dashboard
    total_areas = db.query(Area).count()
    total_users = db.query(User).count()
    total_events = db.query(CollectionEvent).count()
    
    # Fetch areas for the dropdown in the "Log Event" form
    areas = db.query(Area).all()

    return templates.TemplateResponse(
        request=request, 
        name="admin.html", 
        context={
            "user": current_user,
            "total_areas": total_areas,
            "total_users": total_users,
            "total_events": total_events,
            "areas": areas
        }
    )

@router.post("/admin/add-area")
def add_area(
    request: Request,
    name: str = Form(...),
    ward: str = Form(None),
    landmark: str = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Handles the creation of a new area."""
    
    # Check if area already exists
    existing = db.query(Area).filter(Area.name == name).first()
    if not existing:
        new_area = Area(name=name, ward=ward, landmark=landmark)
        db.add(new_area)
        db.commit()

    return RedirectResponse(url="/admin", status_code=status.HTTP_303_SEE_OTHER)

@router.post("/admin/add-event")
def add_event(
    request: Request,
    area_id: int = Form(...),
    collection_date: date = Form(...),
    actual_time: time = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Handles logging a historical collection event."""
    
    new_event = CollectionEvent(
        area_id=area_id,
        collection_date=collection_date,
        actual_time=actual_time,
        status="completed"
    )
    db.add(new_event)
    db.commit()

    return RedirectResponse(url="/admin", status_code=status.HTTP_303_SEE_OTHER)