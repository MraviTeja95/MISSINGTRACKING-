"""
General helper utilities
"""


def allowed_file(filename: str, allowed_extensions: set) -> bool:
    """Check if the file extension is in the allowed set."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions
