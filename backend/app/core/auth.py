from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from typing import List, Optional

from app.core.config import settings
from app.core.database import get_db
from app.models.user import User, Role, RoleAssignment
from app.schemas.auth import TokenData

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(
            credentials.credentials, 
            settings.JWT_SECRET, 
            algorithms=[settings.JWT_ALGORITHM]
        )
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(username=email)
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.email == token_data.username).first()
    if user is None:
        raise credentials_exception
    
    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def get_user_roles(user: User, db: Session) -> List[Role]:
    """Get all roles for a user"""
    role_assignments = db.query(RoleAssignment).filter(
        RoleAssignment.user_id == user.id
    ).all()
    
    roles = []
    for assignment in role_assignments:
        role = db.query(Role).filter(Role.id == assignment.role_id).first()
        if role:
            roles.append(role)
    
    return roles

def check_permission(required_roles: List[str], user_roles: List[Role]) -> bool:
    """Check if user has any of the required roles"""
    user_role_names = [role.name for role in user_roles]
    return any(role in user_role_names for role in required_roles)

def require_roles(roles: List[str]):
    """Dependency to require specific roles"""
    def role_checker(
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
    ):
        user_roles = get_user_roles(current_user, db)
        if not check_permission(roles, user_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        return current_user
    return role_checker

# Specific role dependencies
require_admin = require_roles(["admin"])
require_publisher = require_roles(["admin", "publisher"])
require_handler = require_roles(["admin", "publisher", "handler"])
require_viewer = require_roles(["admin", "publisher", "handler", "viewer"])