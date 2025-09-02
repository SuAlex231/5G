from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    is_active: Optional[bool] = True

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None

class User(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class RoleBase(BaseModel):
    name: str
    description: Optional[str] = None
    permissions: dict = {}

class RoleCreate(RoleBase):
    pass

class Role(RoleBase):
    id: int

    class Config:
        from_attributes = True

class RoleAssignmentBase(BaseModel):
    user_id: int
    role_id: int

class RoleAssignmentCreate(RoleAssignmentBase):
    pass

class RoleAssignment(RoleAssignmentBase):
    id: int
    created_at: datetime
    role: Role

    class Config:
        from_attributes = True

class UserWithRoles(User):
    role_assignments: List[RoleAssignment] = []