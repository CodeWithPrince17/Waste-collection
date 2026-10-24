from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from fastapi import status

from app.database import get_db
from app.auth import get_current_user
from app.models import User, Area

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/resident", response_class=HTMLResponse)
def resident_dashboard(
    request: Request, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Serves the resident dashboard."""
    
    # Security check: Ensure an admin isn't accidentally viewing the resident page
    if current_user.role == "admin":
        return RedirectResponse(url="/admin", status_code=status.HTTP_303_SEE_OTHER)

    # Fetch all areas so the user can select one from a dropdown
    areas = db.query(Area).all()

    return templates.TemplateResponse(
        request=request, 
        name="resident.html", 
        context={"user": current_user, "areas": areas}
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