import secrets

import redis as redis_lib

from backend.config.paths import REDIS_URL

_redis = redis_lib.from_url(REDIS_URL)
_TOKEN_TTL_SECONDS = 86400  # 24 hours — cancel link lifetime
_COMPLETED_TTL_SECONDS = 7  # 7 days — task completed marker lifetime


def generate_cancel_token(task_uid: str) -> str:
    token = secrets.token_urlsafe(32)
    _redis.setex(f"cancel_token:{task_uid}", _TOKEN_TTL_SECONDS, token)
    return token


def verify_and_consume_cancel_token(task_uid: str, token: str) -> bool:
    key = f"cancel_token:{task_uid}"
    stored = _redis.get(key)
    if stored is None:
        return False
    if stored.decode() == token:
        _redis.delete(key)
        return True
    return False


def mark_task_completed(task_uid: str) -> None:
    """Call from Celery task finally-block to invalidate the cancel link."""
    _redis.delete(f"cancel_token:{task_uid}")
    _redis.setex(f"task_completed:{task_uid}", _COMPLETED_TTL_SECONDS, "1")


def is_task_completed(task_uid: str) -> bool:
    return bool(_redis.exists(f"task_completed:{task_uid}"))
