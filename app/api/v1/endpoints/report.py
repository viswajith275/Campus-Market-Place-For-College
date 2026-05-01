from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.models.user import User
from app.schemas import report
from app.services import report_service

router = APIRouter()


@router.post("/{item_id}")
async def report_item(
    request: Request,
    report_request: report.ReportCreate,
    item_id: int,
    current_user: User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(deps.get_db),
):
    return await report_service.report_item(
        report_request=report_request, item_id=item_id, user_id=current_user.id, db=db
    )
