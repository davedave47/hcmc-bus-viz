"""Small thread-safe TTL + LRU cache for read-only warehouse results.

The warehouse is read-only between rebuilds, so caching computed chart payloads
by (theme, slug, filters) avoids re-scanning Gold/fact tables on every request.
A short TTL bounds staleness after a rebuild without a manual invalidation hook.
"""
from __future__ import annotations

import threading
import time
from collections import OrderedDict
from collections.abc import Callable, Hashable
from typing import Generic, TypeVar

T = TypeVar("T")


class TTLCache(Generic[T]):
    def __init__(self, maxsize: int = 256, ttl: float = 300.0) -> None:
        self._maxsize = maxsize
        self._ttl = ttl
        self._store: OrderedDict[Hashable, tuple[float, T]] = OrderedDict()
        self._lock = threading.Lock()

    def get_or_compute(self, key: Hashable, compute: Callable[[], T]) -> T:
        now = time.monotonic()
        with self._lock:
            hit = self._store.get(key)
            if hit is not None and now - hit[0] < self._ttl:
                self._store.move_to_end(key)
                return hit[1]
        value = compute()  # computed outside the lock (avoids serialising slow queries)
        with self._lock:
            self._store[key] = (now, value)
            self._store.move_to_end(key)
            while len(self._store) > self._maxsize:
                self._store.popitem(last=False)
        return value

    def clear(self) -> None:
        with self._lock:
            self._store.clear()
