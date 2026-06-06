import time

from busanalytics_api.core.cache import TTLCache


def test_caches_and_computes_once() -> None:
    cache: TTLCache[int] = TTLCache(maxsize=8, ttl=60)
    calls = {"n": 0}

    def compute() -> int:
        calls["n"] += 1
        return 42

    assert cache.get_or_compute("k", compute) == 42
    assert cache.get_or_compute("k", compute) == 42
    assert calls["n"] == 1  # second hit served from cache


def test_ttl_expiry_recomputes() -> None:
    cache: TTLCache[int] = TTLCache(maxsize=8, ttl=0.01)
    calls = {"n": 0}

    def compute() -> int:
        calls["n"] += 1
        return calls["n"]

    assert cache.get_or_compute("k", compute) == 1
    time.sleep(0.02)
    assert cache.get_or_compute("k", compute) == 2  # expired -> recomputed


def test_lru_eviction() -> None:
    cache: TTLCache[int] = TTLCache(maxsize=2, ttl=60)
    cache.get_or_compute("a", lambda: 1)
    cache.get_or_compute("b", lambda: 2)
    cache.get_or_compute("c", lambda: 3)  # evicts "a" (oldest)
    recomputed = {"n": 0}

    def compute_a() -> int:
        recomputed["n"] += 1
        return 1

    cache.get_or_compute("a", compute_a)
    assert recomputed["n"] == 1  # "a" was evicted, so recomputed
