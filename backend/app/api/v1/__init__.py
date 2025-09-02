from fastapi import APIRouter
from .auth import router as auth_router
from .users import router as users_router
from .roles import router as roles_router
from .tickets import router as tickets_router
from .ticket_types import router as ticket_types_router

api_router = APIRouter()

# Include all route modules
api_router.include_router(auth_router, prefix="/auth", tags=["authentication"])
api_router.include_router(users_router, prefix="/users", tags=["users"])
api_router.include_router(roles_router, prefix="/roles", tags=["roles"])
api_router.include_router(tickets_router, prefix="/tickets", tags=["tickets"])
api_router.include_router(ticket_types_router, prefix="/ticket-types", tags=["ticket-types"])