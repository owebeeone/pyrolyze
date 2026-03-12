"""Import-discovery and cache helpers for transformed module artifacts."""

from __future__ import annotations

import hashlib
import pickle
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any



def compute_source_fingerprint(source: str, *, mtime: int | float, python_magic: str) -> str:
    payload = f"{python_magic}|{mtime}|{source}".encode("utf-8")
    return hashlib.sha256(payload).hexdigest()



def should_transform(
    *,
    module_name: str,
    file_path: str,
    source_text: str,
) -> bool:
    """Enable transformation when the source opts in with '#@pyrolyze'."""
    del module_name, file_path  # reserved for future filters
    lines = source_text.splitlines()
    marker_window = lines[:2]
    return any(line.strip() == "#@pyrolyze" for line in marker_window)


@dataclass
class BytecodeCache:
    """In-memory cache keyed by module name and cache key."""

    _entries: dict[str, tuple[str, Any]] = field(default_factory=dict)

    def put(self, *, module_name: str, cache_key: str, payload: Any) -> None:
        self._entries[module_name] = (cache_key, payload)

    def get(self, *, module_name: str, cache_key: str) -> Any | None:
        record = self._entries.get(module_name)
        if record is None:
            return None

        stored_key, payload = record
        if stored_key != cache_key:
            return None

        return payload


@dataclass
class PersistentArtifactCache:
    """Disk-backed cache for transformed artifacts keyed by module and cache key."""

    cache_dir: str | Path

    def __post_init__(self) -> None:
        self._root = Path(self.cache_dir)
        self._root.mkdir(parents=True, exist_ok=True)

    def put(self, *, module_name: str, cache_key: str, payload: Any) -> None:
        cache_path = self._module_cache_path(module_name)
        record = {
            "cache_key": cache_key,
            "payload": payload,
        }
        with cache_path.open("wb") as fh:
            pickle.dump(record, fh)

    def get(self, *, module_name: str, cache_key: str) -> Any | None:
        cache_path = self._module_cache_path(module_name)
        if not cache_path.exists():
            return None

        try:
            with cache_path.open("rb") as fh:
                record = pickle.load(fh)
        except Exception:
            return None

        if not isinstance(record, dict):
            return None

        if record.get("cache_key") != cache_key:
            return None

        return record.get("payload")

    def _module_cache_path(self, module_name: str) -> Path:
        safe_name = (
            module_name.replace(".", "__")
            .replace("/", "_")
            .replace("\\", "_")
            .replace(":", "_")
        )
        digest = hashlib.sha1(module_name.encode("utf-8")).hexdigest()[:10]
        return self._root / f"{safe_name}.{digest}.pyrolyze-cache"


__all__ = [
    "BytecodeCache",
    "PersistentArtifactCache",
    "compute_source_fingerprint",
    "should_transform",
]
