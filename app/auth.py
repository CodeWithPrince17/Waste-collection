from fastapi import APIRouter, Depends, HTTPException, Request, status, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.security import verify_password, get_password_hash
from app.schemas import UserCreate

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# ---------------------------------------------------------
# DEPENDENCIES (The Security Guards)
# ---------------------------------------------------------

def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    """Checks the session cookie. Returns the User object or raises an error."""
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Not authenticated"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Checks if the logged-in user is an admin."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Admin privileges required"
        )
    return current_user

# ---------------------------------------------------------
# ROUTES (The HTTP Endpoints)
# ---------------------------------------------------------

@router.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    """Serves the registration form."""
    return templates.TemplateResponse(request=request, name="register.html")

@router.post("/register")
def register_user(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    """Handles form submission for registration."""
    # 1. Check if email already exists
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        # For now, we'll just return a simple error string. 
        # Later we can make a proper HTML error page.
        return templates.TemplateResponse(
            request=request, name="register.html", 
            context={"error": "Email already registered"}
        )

    # 2. Hash the password and create the user
    new_user = User(
        name=name,
        email=email,
        password_hash=get_password_hash(password),
        role="resident" # Default role for new signups
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # 3. Redirect to login page after successful registration
    return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    """Serves the login form."""
    return templates.TemplateResponse(request=request, name="login.html")

@router.post("/login")
def login_user(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    """Handles form submission for login."""
    user = db.query(User).filter(User.email == email).first()
    
    # Verify user exists AND password is correct
    if not user or not verify_password(password, user.password_hash):
        return templates.TemplateResponse(
            request=request, name="login.html", 
            context={"error": "Invalid email or password"}
        )

    # SET THE SESSION COOKIE (Log them in)
    request.session["user_id"] = user.id
    request.session["role"] = user.role

    # Redirect based on role
    if user.role == "admin":
        return RedirectResponse(url="/admin", status_code=status.HTTP_303_SEE_OTHER)
    else:
        return RedirectResponse(url="/resident", status_code=status.HTTP_303_SEE_OTHER)

@router.get("/logout")
def logout_user(request: Request):
    """Clears the session and redirects to login."""
    request.session.clear()
    return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)