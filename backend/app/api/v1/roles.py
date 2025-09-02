from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List

from ...core.database import get_session
from ...core.deps import require_admin, get_current_active_user
from ...models.models import Role, RoleEnum
from ...schemas.schemas import RoleResponse

router = APIRouter()


@router.get("/", response_model=List[RoleResponse])
async def list_roles(
    current_user = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """List all roles."""
    statement = select(Role)
    roles = session.exec(statement).all()
    return [RoleResponse.model_validate(role) for role in roles]