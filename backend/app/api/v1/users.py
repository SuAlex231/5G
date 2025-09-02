from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.auth import require_admin, get_current_active_user
from app.core.security import get_password_hash
from app.models.user import User, Role, RoleAssignment
from app.schemas.user import User as UserSchema, UserCreate, UserUpdate, UserWithRoles

router = APIRouter()

@router.get("/", response_model=List[UserWithRoles])
async def list_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
    skip: int = 0,
    limit: int = 100
):
    """List all users (admin only)"""
    users = db.query(User).offset(skip).limit(limit).all()
    
    # Add role information to each user
    result = []
    for user in users:
        user_data = UserWithRoles.from_orm(user)
        # Get role assignments
        role_assignments = db.query(RoleAssignment).filter(
            RoleAssignment.user_id == user.id
        ).all()
        user_data.role_assignments = role_assignments
        result.append(user_data)
    
    return result

@router.post("/", response_model=UserSchema)
async def create_user(
    user: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Create a new user (admin only)"""
    # Check if user already exists
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        password_hash=hashed_password,
        full_name=user.full_name,
        is_active=user.is_active
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

@router.get("/{user_id}", response_model=UserWithRoles)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get user by ID"""
    # Users can view their own profile, admins can view any
    if current_user.id != user_id:
        # Check if current user is admin
        from app.core.auth import get_user_roles, check_permission
        user_roles = get_user_roles(current_user, db)
        if not check_permission(["admin"], user_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Get role assignments
    user_data = UserWithRoles.from_orm(user)
    role_assignments = db.query(RoleAssignment).filter(
        RoleAssignment.user_id == user.id
    ).all()
    user_data.role_assignments = role_assignments
    
    return user_data

@router.put("/{user_id}", response_model=UserSchema)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update user"""
    # Users can update their own profile, admins can update any
    if current_user.id != user_id:
        from app.core.auth import get_user_roles, check_permission
        user_roles = get_user_roles(current_user, db)
        if not check_permission(["admin"], user_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update fields
    update_data = user_update.dict(exclude_unset=True)
    if "password" in update_data:
        update_data["password_hash"] = get_password_hash(update_data.pop("password"))
    
    for field, value in update_data.items():
        setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    
    return user

@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Delete user (admin only)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Don't allow deleting self
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete yourself"
        )
    
    # Delete role assignments first
    db.query(RoleAssignment).filter(RoleAssignment.user_id == user_id).delete()
    
    # Delete user
    db.delete(user)
    db.commit()
    
    return {"message": "User deleted successfully"}