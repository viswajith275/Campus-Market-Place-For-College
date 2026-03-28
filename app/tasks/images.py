from pathlib import Path

from app.core.celery import celery_app


@celery_app.task
def delete_image_task(image_path: str):

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
