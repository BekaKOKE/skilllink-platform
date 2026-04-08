import time
import cProfile
import pstats
import io
import os
import logging
from collections import defaultdict

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("skilllink")

PROFILING_ENABLED = os.getenv("PROFILING_ENABLED", "true").lower() == "true"
SLOW_THRESHOLD_MS = float(os.getenv("SLOW_THRESHOLD_MS", "500"))

# Хранилище латентностей: endpoint -> [ms, ...]
_latency_store: dict = defaultdict(list)


def get_latency_report() -> dict:
    report = {}
    for endpoint, times in _latency_store.items():
        if not times:
            continue
        report[endpoint] = {
            "count": len(times),
            "avg_ms": round(sum(times) / len(times), 2),
            "max_ms": round(max(times), 2),
            "min_ms": round(min(times), 2),
        }
    return report


class ProfilingMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next) -> Response:
        endpoint = request.url.path
        method = request.method
        start = time.perf_counter()

        if PROFILING_ENABLED:
            profiler = cProfile.Profile()
            profiler.enable()
            try:
                response = await call_next(request)
            finally:
                profiler.disable()

            elapsed_ms = (time.perf_counter() - start) * 1000
            _latency_store[endpoint].append(elapsed_ms)

            # Топ-10 функций по cumulative time
            stream = io.StringIO()
            ps = pstats.Stats(profiler, stream=stream)
            ps.strip_dirs().sort_stats("cumulative").print_stats(10)
            logger.debug(
                f"[PROFILER] {method} {endpoint} — {elapsed_ms:.2f}ms\n"
                f"{stream.getvalue()}"
            )
        else:
            response = await call_next(request)
            elapsed_ms = (time.perf_counter() - start) * 1000
            _latency_store[endpoint].append(elapsed_ms)

        # Предупреждение если эндпоинт медленный
        if elapsed_ms > SLOW_THRESHOLD_MS:
            logger.warning(
                f"[SLOW] {method} {endpoint} — {elapsed_ms:.2f}ms "
                f"(threshold={SLOW_THRESHOLD_MS}ms)"
            )

        response.headers["X-Processing-Time-Ms"] = f"{elapsed_ms:.2f}"
        return response