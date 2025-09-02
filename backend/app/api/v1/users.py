from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List

from ...core.database import get_session
from ...core.deps import require_admin, get_current_active_user, require_any_role
from ...models.models import User, Role, RoleAssignment, RoleEnum
from ...schemas.schemas import UserResponse, UserCreate, UserUpdate, RoleResponse
from ...core.security import get_password_hash

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """Get current user information."""
    # Get user roles
    statement = select(Role.name).join(RoleAssignment).where(
        RoleAssignment.user_id == current_user.id
    )
    roles = session.exec(statement).all()
    
    user_response = UserResponse.model_validate(current_user)
    user_response.roles = [role.value for role in roles]
    return user_response


@router.get("/", response_model=List[UserResponse])
async def list_users(
    current_user: User = Depends(require_admin),
    session: Session = Depends(get_session),
    skip: int = 0,
    limit: int = 100
):
    """List all users (admin only)."""
    statement = select(User).offset(skip).limit(limit)
    users = session.exec(statement).all()
    
    user_responses = []
    for user in users:
        # Get roles for each user
        role_statement = select(Role.name).join(RoleAssignment).where(
            RoleAssignment.user_id == user.id
        )
        roles = session.exec(role_statement).all()
        
        user_response = UserResponse.model_validate(user)
        user_response.roles = [role.value for role in roles]
        user_responses.append(user_response)
    
    return user_responses


@router.post("/", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    current_user: User = Depends(require_admin),
    session: Session = Depends(get_session)
):
    """Create a new user (admin only)."""
    # Check if email already exists
    existing_user = session.exec(select(User).where(User.email == user_data.email)).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Check if username already exists
    existing_username = session.exec(select(User).where(User.username == user_data.username)).first()
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # Create user
    hashed_password = get_password_hash(user_data.password)
    user = User(
        email=user_data.email,
        username=user_data.username,
        full_name=user_data.full_name,
        hashed_password=hashed_password
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    
    # Assign default viewer role
    viewer_role = session.exec(select(Role).where(Role.name == RoleEnum.VIEWER)).first()
    if viewer_role:
        role_assignment = RoleAssignment(user_id=user.id, role_id=viewer_role.id)
        session.add(role_assignment)
        session.commit()
    
    return UserResponse.model_validate(user, update={"roles": ["viewer"]})


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    current_user: User = Depends(require_admin),
    session: Session = Depends(get_session)
):
    """Update user (admin only)."""
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update user fields
    update_data = user_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    
    session.add(user)
    session.commit()
    session.refresh(user)
    
    # Get user roles
    statement = select(Role.name).join(RoleAssignment).where(
        RoleAssignment.user_id == user.id
    )
    roles = session.exec(statement).all()
    
    user_response = UserResponse.model_validate(user)
    user_response.roles = [role.value for role in roles]
    return user_response


@router.post("/{user_id}/roles/{role_name}")
async def assign_role(
    user_id: int,
    role_name: RoleEnum,
    current_user: User = Depends(require_admin),
    session: Session = Depends(get_session)
):
    """Assign role to user (admin only)."""
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    role = session.exec(select(Role).where(Role.name == role_name)).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    
    # Check if assignment already exists
    existing = session.exec(
        select(RoleAssignment).where(
            RoleAssignment.user_id == user_id,
            RoleAssignment.role_id == role.id
        )
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role already assigned to user"
        )
    
    # Create role assignment
    role_assignment = RoleAssignment(user_id=user_id, role_id=role.id)
    session.add(role_assignment)
    session.commit()
    
    return {"message": f"Role {role_name} assigned to user"}


@router.delete("/{user_id}/roles/{role_name}")
async def remove_role(
    user_id: int,
    role_name: RoleEnum,
    current_user: User = Depends(require_admin),
    session: Session = Depends(get_session)
):
    """Remove role from user (admin only)."""
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    role = session.exec(select(Role).where(Role.name == role_name)).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    
    # Find and remove role assignment
    assignment = session.exec(
        select(RoleAssignment).where(
            RoleAssignment.user_id == user_id,
            RoleAssignment.role_id == role.id
        )
    ).first()
    
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not assigned to user"
        )
    
    session.delete(assignment)
    session.commit()
    
    return {"message": f"Role {role_name} removed from user"}