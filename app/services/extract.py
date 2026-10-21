import os
import io
import re
from werkzeug.utils import secure_filename
import pypdf

ALLOWED_EXTENSIONS = {"txt", "pdf"}
MIN_CHAR_COUNT = 200
MAX_CHAR_COUNT = 50000


class ExtractError(Exception):
    """Base exception for extraction errors."""
    pass


class ScannedPDFError(ExtractError):
    """Raised when PDF text extraction produces no usable text."""
    pass


class ValidationError(ExtractError):
    """Raised when text does not satisfy length or validation constraints."""
    pass


def allowed_file(filename: str) -> bool:
    if not filename or "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[1].lower()
    return ext in ALLOWED_EXTENSIONS


def normalize_text(text: str) -> str:
    if not text:
        return ""
    # Normalize line breaks and multiple spaces
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    # Replace non-printable characters except standard whitespace
    text = re.sub(r"[^\x20-\x7E\n\t]", " ", text)
    # Collapse excess whitespace
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def validate_text_length(text: str) -> str:
    cleaned = normalize_text(text)
    char_len = len(cleaned)
    if char_len < MIN_CHAR_COUNT:
        raise ValidationError(
            f"Note content is too short ({char_len} characters). Minimum required is {MIN_CHAR_COUNT} characters."
        )
    if char_len > MAX_CHAR_COUNT:
        raise ValidationError(
            f"Note content is too long ({char_len} characters). Maximum allowed is {MAX_CHAR_COUNT} characters."
        )
    return cleaned


def extract_from_file(file_storage) -> tuple[str, str, str]:
    """
    Extracts text from an uploaded Werkzeug FileStorage object.
    Returns: (extracted_text, filename, source_type)
    """
    if not file_storage or not file_storage.filename:
        raise ValidationError("No file was uploaded.")

    filename = secure_filename(file_storage.filename)
    if not allowed_file(filename):
        raise ValidationError("Invalid file type. Only .txt and .pdf files are accepted.")

    ext = filename.rsplit(".", 1)[1].lower()
    raw_bytes = file_storage.read()

    if not raw_bytes:
        raise ValidationError("The uploaded file is empty.")

    extracted_text = ""

    if ext == "txt":
        try:
            extracted_text = raw_bytes.decode("utf-8")
        except UnicodeDecodeError:
            try:
                extracted_text = raw_bytes.decode("latin-1")
            except Exception as e:
                raise ExtractError(f"Could not read text file: {e}")
        source_type = "txt"

    elif ext == "pdf":
        try:
            reader = pypdf.PdfReader(io.BytesIO(raw_bytes))
            pages_text = []
            for page in reader.pages:
                page_t = page.extract_text()
                if page_t:
                    pages_text.append(page_t)
            extracted_text = "\n".join(pages_text).strip()
        except Exception as e:
            raise ExtractError(f"Failed to parse PDF file: {e}")

        if not extracted_text:
            raise ScannedPDFError(
                "This PDF looks scanned; please upload a text-based PDF or paste the text."
            )
        source_type = "pdf"
    else:
        raise ValidationError("Unsupported file format.")

    validated = validate_text_length(extracted_text)
    return validated, filename, source_type
