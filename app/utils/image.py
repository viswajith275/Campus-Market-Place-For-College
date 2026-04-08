import io
import uuid
from pathlib import Path

import magic
from PIL import Image, ImageOps

from app.core.config import settings
from app.core.exceptions import BadRequest

allowed_types = {"image/jpeg", "image/png", "image/webp"}


async def save_and_validate_raw_image(image) -> Path:
    first_chunk = await image.read(2048)
    actual_mime_type = magic.from_buffer(first_chunk, mime=True)
    if actual_mime_type not in allowed_types:
        raise BadRequest(f"Unsupported media type. Allowed: {allowed_types}")
    await image.seek(0)

    raw_filename = f"raw_{uuid.uuid4()}.bin"
    raw_path = Path(settings.raw_upload_directory / raw_filename)
    saved_bytes = 0

    try:
        with open(raw_path, "wb") as out:
            while chunk := await image.read(1024 * 1024):
                saved_bytes += len(chunk)
                if saved_bytes > settings.max_image_size:
                    raise BadRequest(
                        f"File exceeds maximum allowed size of "
                        f"{settings.max_image_size / 1024 / 1024:.1f} MB."
                    )
                out.write(chunk)

    except Exception as e:
        safe_remove(raw_path)
        raise e

    try:
        with open(raw_path, "rb") as i:
            img: Image.Image = Image.open(i)
            img.verify()
    except Exception:
        safe_remove(raw_path)
        raise BadRequest("Uploaded file is not a valid or readable image.")

    return raw_path


def process_raw_image(raw_path: Path) -> Path:

    with open(raw_path, "rb") as i:
        data = i.read()

    img = Image.open(io.BytesIO(data))

    if img.mode not in ("RGB", "RGBA"):
        img = img.convert("RGBA" if "A" in img.mode else "RGB")

    img = strip_exif_metadata(img)

    img = resize(img, 1200)

    img = prepare_for_webp_format(img)

    final_filename = f"{uuid.uuid4()}.webp"
    final_path = Path(settings.upload_directory / final_filename)
    img.save(
        final_path,
        format="WEBP",
        quality=settings.webp_quality,
        method=6,
    )

    return final_path


def strip_exif_metadata(img: Image.Image) -> Image.Image:

    img = ImageOps.exif_transpose(img)

    clean = Image.new(img.mode, img.size)
    clean.paste(img)
    return clean


def resize(img: Image.Image, max_dim: int) -> Image.Image:

    if img.size[0] <= max_dim and img.size[1] <= max_dim:
        return img

    img.thumbnail((max_dim, max_dim), Image.Resampling.LANCZOS)
    return img


def prepare_for_webp_format(img: Image.Image) -> Image.Image:
    if img.mode == "RGBA":
        background = Image.new("RGB", img.size, (255, 255, 255))
        background.paste(img, mask=img.split()[3])  # 3 is the alpha channel A in RGBA
        return background
    return img.convert("RGB") if img.mode != "RGB" else img


def safe_remove(path: Path) -> None:
    path = Path(path)
    try:
        if path.exists():
            path.unlink(missing_ok=True)
    except Exception as e:
        raise e
