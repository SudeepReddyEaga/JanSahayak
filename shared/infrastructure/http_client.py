"""
Shared Loop-Aware Asynchronous HTTP Connection Pool (DRY + Performance Helper).
Reuses persistent HTTP/1.1 keep-alive TCP connections per active asyncio event loop,
eliminating repetitive per-call socket handshakes across microservice HTTP boundaries.
"""

import asyncio
import httpx


class LoopAwareAsyncHttpPool:
    """
    Maintains a persistent httpx.AsyncClient bound safely to the active running
    asyncio event loop so inter-microservice calls stay fast (<2 ms overhead) while
    remaining safe across loop restarts in unit/integration tests.
    """

    def __init__(self, timeout_seconds: float = 30.0) -> None:
        self._timeout = timeout_seconds
        self._loop: asyncio.AbstractEventLoop | None = None
        self._client: httpx.AsyncClient | None = None

    def get_client(self) -> httpx.AsyncClient:
        """Return an open keep-alive AsyncClient bound to the current running loop."""
        running_loop = asyncio.get_running_loop()
        if self._client is None or self._client.is_closed or self._loop is not running_loop:
            limits = httpx.Limits(max_connections=32, max_keepalive_connections=16)
            self._client = httpx.AsyncClient(timeout=self._timeout, limits=limits)
            self._loop = running_loop
        return self._client

