"""Signal helper — Boundary Hardening V1.

Signals are the correct abstraction for LabOS. A signal says
"here is a domain observation" — not "here is what should happen next".

Decisions (planning, orchestration, prioritization) belong to ABrain.
LabOS only:
- produces signals from telemetry/vision/safety/state,
- validates and executes commanded actions,
- enforces local safety guards.

V1 scope: no persistence. `emit_signal()` is a pure, deterministic
constructor. Callers use the returned dict as part of structured
responses so the adapter layer can forward it to ABrain as context.
"""
from __future__ import annotations

from typing import Any


def emit_signal(signal_type: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    return {
        'type': signal_type,
        'payload': dict(payload) if payload else {},
    }
