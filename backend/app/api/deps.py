# Этот файл оставлен для обратной совместимости.
# Используйте backend.app.core.dependencies напрямую.
from backend.app.core.dependencies import get_db, get_current_user, require_role

__all__ = ["get_db", "get_current_user", "require_role"]