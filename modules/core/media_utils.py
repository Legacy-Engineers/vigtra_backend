import os
from django.core.files.storage import default_storage
from PIL import Image
import uuid


def validate_file_size(file, max_size):
    """Validate file size"""
    if file.size > max_size:
        raise ValueError(f"File size exceeds maximum allowed size of {max_size} bytes")
    return True


def validate_file_extension(file, allowed_extensions):
    """Validate file extension"""
    ext = os.path.splitext(file.name)[1].lower()
    if ext not in allowed_extensions:
        raise ValueError(
            f"File extension {ext} not allowed. Allowed extensions: {', '.join(allowed_extensions)}"
        )
    return True


def generate_unique_filename(original_filename):
    """Generate unique filename while preserving extension"""
    ext = os.path.splitext(original_filename)[1]
    return f"{uuid.uuid4()}{ext}"


def create_thumbnail(image_path, thumbnail_path, size=(150, 150)):
    """Create thumbnail from image"""
    try:
        with Image.open(image_path) as img:
            img.thumbnail(size, Image.Resampling.LANCZOS)
            img.save(thumbnail_path, optimize=True, quality=85)
        return True
    except Exception as e:
        print(f"Error creating thumbnail: {e}")
        return False


def delete_file_if_exists(file_path):
    """Delete file if it exists"""
    if default_storage.exists(file_path):
        default_storage.delete(file_path)
        return True
    return False


def get_file_info(file_field):
    """Get file information"""
    if not file_field:
        return None

    file_path = file_field.path if hasattr(file_field, "path") else str(file_field)
    file_size = file_field.size if hasattr(file_field, "size") else 0
    file_name = os.path.basename(file_path)
    file_ext = os.path.splitext(file_name)[1].lower()

    return {
        "name": file_name,
        "path": file_path,
        "size": file_size,
        "extension": file_ext,
        "size_formatted": format_file_size(file_size),
    }


def format_file_size(size_bytes):
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0 B"

    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1

    return f"{size_bytes:.1f} {size_names[i]}"


class MediaUploadHandler:
    """Handle media uploads with validation and processing"""

    def __init__(self, allowed_extensions=None, max_size=None):
        self.allowed_extensions = allowed_extensions or []
        self.max_size = max_size

    def validate_and_process(self, file):
        """Validate and process uploaded file"""
        # Validate file extension
        if self.allowed_extensions:
            validate_file_extension(file, self.allowed_extensions)

        # Validate file size
        if self.max_size:
            validate_file_size(file, self.max_size)

        # Generate unique filename
        unique_name = generate_unique_filename(file.name)
        file.name = unique_name

        return file
