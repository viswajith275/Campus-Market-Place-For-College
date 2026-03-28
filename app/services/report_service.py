from typing import Dict

from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BadRequest, NotFound
from app.models.enum import NotificationType
from app.models.item import Item
from app.models.report import Report
from app.schemas.report import ReportCreate
from app.services.notification_service import notify


async def report_item(
    report_request: ReportCreate, item_id: int, user_id: int, db: AsyncSession
) -> Dict:

    result = await db.execute(select(Item).where(Item.id == item_id))

    item = result.scalar_one_or_none()

    if item is None:
        raise NotFound("Item not found!")

    if item.seller_id == user_id:
        raise BadRequest("You cannot report your own item!")

    result = await db.execute(
        select(exists().where(Report.item_id == item_id, Report.reporter_id == user_id))
    )
    existing = result.scalar_one_or_none()

    if existing:
        raise BadRequest("Cannot report an item twice!")

    new_report = Report(
        category=report_request.category,
        description=report_request.description,
        item_id=item_id,
        reporter_id=user_id,
    )

    db.add(new_report)
    await db.commit()

    notify(
        user_id=str(user_id),
        title="Reported successfully",
        message=f"Item {item.title} has been reported successfully for {report_request.category.value}",
        type=NotificationType.Reported_Successfully,
    )

    return {"message": "Reported successfully!"}
