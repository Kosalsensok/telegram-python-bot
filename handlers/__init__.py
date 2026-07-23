from .commands import get_command_router
from .callbacks import get_callbacks_router
from .text import get_text_router
from .image import get_image_router
from .document import get_document_router
from .fallback import get_fallback_router
from .admin import get_admin_router

__all__ = [
    "get_command_router",
    "get_callbacks_router",
    "get_text_router",
    "get_image_router",
    "get_document_router",
    "get_fallback_router",
    "get_admin_router"
]

