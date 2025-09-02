from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session, select
from ..core.database import get_session
from ..core.security import verify_token
from ..models.models import User, RoleAssignment, Role, RoleEnum
from typing import List

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: Session = Depends(get_session)
) -> User:
    """Get current authenticated user."""
    token = credentials.credentials
    payload = verify_token(token)
    
    if payload is None or payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
    
    user_id = payload.get("user_id")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
    
    user = session.get(User, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User is inactive"
        )
    
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current active user."""
    return current_user


def require_roles(required_roles: List[RoleEnum]):
    """Create a dependency that requires specific roles."""
    async def role_checker(
        current_user: User = Depends(get_current_active_user),
        session: Session = Depends(get_session)
    ):
        # Get user roles
        statement = select(Role.name).join(RoleAssignment).where(
            RoleAssignment.user_id == current_user.id
        )
        user_roles = session.exec(statement).all()
        
        # Check if user has any of the required roles
        if not any(role in user_roles for role in required_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        
        return current_user
    
    return role_checker


# Convenience dependencies for specific roles
require_admin = require_roles([RoleEnum.ADMIN])
require_admin_or_publisher = require_roles([RoleEnum.ADMIN, RoleEnum.PUBLISHER])
require_admin_or_handler = require_roles([RoleEnum.ADMIN, RoleEnum.HANDLER])
require_any_role = require_roles([RoleEnum.ADMIN, RoleEnum.PUBLISHER, RoleEnum.HANDLER, RoleEnum.VIEWER])