import time

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from backend.app.core.Redis import redis_client

WRITE_METHODS = {"POST", "PUT", "PATCH", "DELETE"}

# Лимиты
LIMIT_PER_MIN = 60
LIMIT_PER_HOUR = 1000
LIMIT_WRITE_PER_HOUR = 20


async def _sliding_window(key: str, window_sec: int, limit: int) -> tuple[bool, int]:
    now = time.time()
    window_start = now - window_sec

    pipe = redis_client.pipeline()
    pipe.zremrangebyscore(key, "-inf", window_start)  # удаляем старые
    pipe.zcard(key)                                    # считаем текущие
    pipe.zadd(key, {str(now): now})                   # добавляем текущий
    pipe.expire(key, window_sec + 10)                 # TTL
    results = await pipe.execute()

    count = results[1]
    allowed = count < limit
    remaining = max(0, limit - count - 1)
    return allowed, remaining


class RateLimitMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next) -> Response:
        forwarded = request.headers.get("X-Forwarded-For")
        ip = forwarded.split(",")[0].strip() if forwarded else (
            request.client.host if request.client else "unknown"
        )
        method = request.method

        # 1. Лимит 60 req/min
        ok, rem_min = await _sliding_window(f"rl:min:{ip}", 60, LIMIT_PER_MIN)
        if not ok:
            return JSONResponse(
                status_code=429,
                content={"detail": "Too many requests. Limit: 60 req/min."},
                headers={"Retry-After": "60"},
            )

        # 2. Лимит 1000 req/hour
        ok, rem_hour = await _sliding_window(f"rl:hr:{ip}", 3600, LIMIT_PER_HOUR)
        if not ok:
            return JSONResponse(
                status_code=429,
                content={"detail": "Too many requests. Limit: 1000 req/hr."},
                headers={"Retry-After": "3600"},
            )

        # 3. Лимит write-запросов 20/hour — только POST/PUT/PATCH/DELETE
        if method in WRITE_METHODS:
            ok, _ = await _sliding_window(f"rl:write:{ip}", 3600, LIMIT_WRITE_PER_HOUR)
            if not ok:
                return JSONResponse(
                    status_code=429,
                    content={"detail": "Too many write requests. Limit: 20 write req/hr."},
                    headers={"Retry-After": "3600"},
                )

        response = await call_next(request)

        # Показываем оставшийся лимит в заголовках
        response.headers["X-RateLimit-Remaining-Min"] = str(rem_min)
        response.headers["X-RateLimit-Remaining-Hour"] = str(rem_hour)

        return response