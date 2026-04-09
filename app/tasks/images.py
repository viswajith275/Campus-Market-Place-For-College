from pathlib import Path

from app.core.celery import worker_celery_app
from app.models.enum import ImageStatus
from app.utils.image import process_raw_image, safe_remove


@worker_celery_app.task(bind=True, max_retries=2)
def delete_image_task(self, image_path: str):

    if not image_path:
        return

    try:
        path = Path(image_path)
        if path.exists() or path.is_file():
            path.unlink()
            return f"Successfully deleted: {path}"
        return f"File not found: {path}"
    except Exception as e:
        raise e


@worker_celery_app.task(bind=True, max_retries=2)
def process_item_image_task(self, raw_path: Path, image_id: int):
    try:
        final_path = process_raw_image(raw_path, 1200)

        from app.db.session import SyncSessionLocal
        from app.models.item_image import ItemImage

        with SyncSessionLocal() as db:
            image_obj = db.get(ItemImage, image_id)
            if image_obj is None:
                safe_remove(final_path)
                safe_remove(raw_path)
                return

            image_obj.status = ImageStatus.Completed
            image_obj.image_path = str(final_path)
            db.commit()

        safe_remove(raw_path)
    except Exception as e:
        raise e


# todo:- add a task for profile picture saving


@worker_celery_app.task(bind=True, max_retries=2)
def process_profile_image_task(self, raw_path: Path, user_id: int):
    try:
        final_path = process_raw_image(raw_path, 800)

        from app.db.session import SyncSessionLocal
        from app.models.user import User

        with SyncSessionLocal() as db:
            user_obj = db.get(User, user_id)
            if user_obj is None:
                safe_remove(final_path)
                safe_remove(raw_path)
                return

            user_obj.image_status = ImageStatus.Completed
            user_obj.image_path = str(final_path)
            db.commit()

        safe_remove(raw_path)
    except Exception as e:
        raise e
