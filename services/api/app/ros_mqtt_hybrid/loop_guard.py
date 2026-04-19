"""Loop prevention for cross-system message routing.

In-memory sliding-window dedup keyed on `message_id`. Bounded size
prevents unbounded growth when the bridges are busy. The guard is
deliberately process-local: LabOS is authoritative, so a restart
resets state and that is fine — worst case is one extra echo on the
very first cycle after restart, which is better than a persistent
duplicate store that can drift from truth.
"""
from __future__ import annotations

from collections import OrderedDict
from threading import Lock


class LoopGuard:
    """Sliding-window dedup cache with hard cap."""

    def __init__(self, max_size: int = 4096):
        self._seen: OrderedDict[str, None] = OrderedDict()
        self._max_size = max_size
        self._lock = Lock()

    def admit(self, message_id: str) -> bool:
        """Return True if the id is new (and accept it), False if seen."""
        if not message_id:
            return True
        with self._lock:
            if message_id in self._seen:
                self._seen.move_to_end(message_id)
                return False
            self._seen[message_id] = None
            if len(self._seen) > self._max_size:
                self._seen.popitem(last=False)
            return True

    def remember(self, message_id: str) -> None:
        if not message_id:
            return
        with self._lock:
            self._seen[message_id] = None
            self._seen.move_to_end(message_id)
            if len(self._seen) > self._max_size:
                self._seen.popitem(last=False)

    def has_seen(self, message_id: str) -> bool:
        if not message_id:
            return False
        with self._lock:
            return message_id in self._seen

    def reset(self) -> None:
        with self._lock:
            self._seen.clear()

    def size(self) -> int:
        with self._lock:
            return len(self._seen)


__all__ = ['LoopGuard']
