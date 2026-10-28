from app.notification import router as notification_router

from contextlib import asynccontextmanager
from app.scheduler import start_scheduler
from app.config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    if settings.scheduler_enabled:
        start_scheduler()
    yield
    # Shutdown logic (optional)



from app.resident import router as resident_router
from app.admin import router as admin_router
from app.prediction import router as prediction_router
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.config import settings
from app.auth import router as auth_router

app = FastAPI(title=settings.app_name, lifespan=lifespan)

# Add Session Middleware (Required for login cookies)
app.add_middleware(SessionMiddleware, secret_key=settings.secret_key)

# Mount static files for CSS/JS
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include the auth router
app.include_router(auth_router)
app.include_router(resident_router)
app.include_router(admin_router)
app.include_router(prediction_router)
app.include_router(notification_router)
@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    # If user is logged in, send them to their dashboard
    if "user_id" in request.session:
        if request.session.get("role") == "admin":
            return RedirectResponse(url="/admin")
        return RedirectResponse(url="/resident")
    
    # If not logged in, send to login page
    return RedirectResponse(url="/login")