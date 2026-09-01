from .auth import router as auth_router
from .events import router as events_router
from .notifications import router as notifications_router
from .teams import router as teams_router
from .users import router as users_router

__all__ = ["auth_router", "events_router", "notifications_router", "teams_router", "users_router"]
