"""Structured runtime tracing for debugging PyRolyze execution."""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from enum import StrEnum
from threading import Lock
from typing import Any, Callable, Iterable, Mapping


class TraceChannel(StrEnum):
    INVALIDATION = "invalidation"
    FLUSH = "flush"
    BOUNDARY = "boundary"
    RECONCILE = "reconcile"


@dataclass(frozen=True, slots=True)
class TraceRecord:
    channel: TraceChannel
    event: str
    fields: Mapping[str, Any] = field(default_factory=dict)


TraceSink = Callable[[TraceRecord], None]
_TRACE_ENV = "PYROLYZE_TRACE"
_TRACE_LOGGER = logging.getLogger("pyrolyze.trace")
_CONFIG_LOCK = Lock()
_ENABLED_CHANNELS: frozenset[TraceChannel] = frozenset()
_TRACE_SINK: TraceSink | None = None


def _normalize_channel(channel: TraceChannel | str) -> TraceChannel:
    if isinstance(channel, TraceChannel):
        return channel
    return TraceChannel(str(channel))


def _normalize_channels(channels: Iterable[TraceChannel | str]) -> frozenset[TraceChannel]:
    return frozenset(_normalize_channel(channel) for channel in channels)


def _default_sink(record: TraceRecord) -> None:
    if record.fields:
        fields = " ".join(f"{key}={value!r}" for key, value in sorted(record.fields.items()))
        _TRACE_LOGGER.info("%s.%s %s", record.channel.value, record.event, fields)
        return
    _TRACE_LOGGER.info("%s.%s", record.channel.value, record.event)


def configure_trace(
    *,
    enabled: Iterable[TraceChannel | str] = (),
    sink: TraceSink | None = None,
) -> None:
    global _ENABLED_CHANNELS, _TRACE_SINK
    with _CONFIG_LOCK:
        _ENABLED_CHANNELS = _normalize_channels(enabled)
        _TRACE_SINK = _default_sink if sink is None else sink


def enable_trace(*channels: TraceChannel | str) -> None:
    global _ENABLED_CHANNELS, _TRACE_SINK
    with _CONFIG_LOCK:
        _ENABLED_CHANNELS = _ENABLED_CHANNELS.union(_normalize_channels(channels))
        if _TRACE_SINK is None:
            _TRACE_SINK = _default_sink


def disable_trace(*channels: TraceChannel | str) -> None:
    global _ENABLED_CHANNELS
    with _CONFIG_LOCK:
        _ENABLED_CHANNELS = _ENABLED_CHANNELS.difference(_normalize_channels(channels))


def reset_trace() -> None:
    global _ENABLED_CHANNELS, _TRACE_SINK
    with _CONFIG_LOCK:
        _ENABLED_CHANNELS = frozenset()
        _TRACE_SINK = None


def configure_trace_from_env(
    env: Mapping[str, str] | None = None,
    *,
    sink: TraceSink | None = None,
) -> frozenset[TraceChannel]:
    raw = (env or os.environ).get(_TRACE_ENV, "")
    channels = tuple(
        _normalize_channel(part.strip())
        for part in raw.split(",")
        if part.strip()
    )
    configure_trace(enabled=channels, sink=sink)
    return frozenset(channels)


def trace_enabled(channel: TraceChannel | str) -> bool:
    return _normalize_channel(channel) in _ENABLED_CHANNELS


def emit_trace(
    channel: TraceChannel | str,
    event: str,
    **fields: Any,
) -> None:
    normalized = _normalize_channel(channel)
    if normalized not in _ENABLED_CHANNELS:
        return
    sink = _TRACE_SINK or _default_sink
    sink(TraceRecord(channel=normalized, event=event, fields=dict(fields)))


configure_trace_from_env()


__all__ = [
    "TraceChannel",
    "TraceRecord",
    "TraceSink",
    "configure_trace",
    "configure_trace_from_env",
    "disable_trace",
    "emit_trace",
    "enable_trace",
    "reset_trace",
    "trace_enabled",
]
