import hashlib
import io
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from PIL import Image, ImageEnhance, ImageOps
from frontend.config import ALLOWED_MIME_TYPES, MAX_FILE_SIZE_MB, SUPPORTED_EXTENSIONS


def compute_file_hash(file_bytes: bytes) -> str:
    """Calculate SHA-256 fingerprint for duplicate detection"""
    return hashlib.sha256(file_bytes).hexdigest()


def format_file_size(size_bytes: int) -> str:
    """Format bytes into readable KB or MB"""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.2f} MB"


def validate_file(filename: str, file_bytes: bytes) -> Tuple[bool, Optional[str]]:
    """Validate file extension, size, and binary integrity"""
    # Check extension
    ext = Path(filename).suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        return False, f"Unsupported file extension '{ext}'. Allowed: {', '.join(SUPPORTED_EXTENSIONS)}"

    # Check file size
    size_mb = len(file_bytes) / (1024 * 1024)
    if size_mb > MAX_FILE_SIZE_MB:
        return False, f"File size ({size_mb:.1f} MB) exceeds maximum allowed limit ({MAX_FILE_SIZE_MB} MB)."

    if len(file_bytes) == 0:
        return False, "Uploaded file is empty (0 bytes)."

    # Verify binary integrity
    if ext in [".jpg", ".jpeg", ".png"]:
        try:
            with Image.open(io.BytesIO(file_bytes)) as img:
                img.verify()
        except Exception:
            return False, "Corrupted or invalid image file."
    elif ext == ".pdf":
        try:
            import pypdfium2 as pdfium
            pdf = pdfium.PdfDocument(file_bytes)
            if len(pdf) == 0:
                return False, "PDF contains zero readable pages."
        except Exception:
            return False, "Corrupted or password-protected PDF document."

    return True, None


def get_pdf_metadata(file_bytes: bytes) -> Dict[str, Any]:
    """Extract page count and text preview stats from PDF"""
    import pypdfium2 as pdfium
    pdf = pdfium.PdfDocument(file_bytes)
    page_count = len(pdf)
    has_text = False

    try:
        text = pdf[0].get_textpage().get_text_range()
        if len(text.strip()) > 30:
            has_text = True
    except Exception:
        pass

    return {
        "page_count": page_count,
        "is_digital_pdf": has_text
    }


def render_pdf_page_to_image(file_bytes: bytes, page_number: int = 0, scale: float = 2.0) -> Image.Image:
    """Render a specific PDF page into a high-DPI PIL Image for preview or vision OCR"""
    import pypdfium2 as pdfium
    pdf = pdfium.PdfDocument(file_bytes)
    if page_number < 0 or page_number >= len(pdf):
        page_number = 0
    page = pdf[page_number]
    return page.render(scale=scale).to_pil()


def preprocess_image_for_ocr(
    image: Image.Image,
    enhance_contrast: bool = True,
    max_pixels: int = 25_000_000
) -> Image.Image:
    """Auto-orient, scale, and enhance contrast for improved optical character recognition"""
    # Auto-orient based on EXIF tag
    try:
        image = ImageOps.exif_transpose(image)
    except Exception:
        pass

    # Ensure RGB
    if image.mode != "RGB":
        image = image.convert("RGB")

    # Scale if exceeding pixel boundary
    pixels = image.width * image.height
    if pixels > max_pixels:
        scale = (max_pixels / pixels) ** 0.5
        new_size = (int(image.width * scale), int(image.height * scale))
        image = image.resize(new_size, Image.LANCZOS)

    # Optional contrast enhancement for faint scans
    if enhance_contrast:
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.2)

    return image
