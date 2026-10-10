"""Offline validation and recoverable promotion of owned generated directories.

Callers must exclude imports, builds, and other maintenance operations. This is
not a live-update protocol or a power-loss durability guarantee.
"""

from __future__ import annotations

import ast
from collections.abc import Mapping
from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path, PurePosixPath
import shutil


def generation_inventory_source(sources: Mapping[str, str]) -> str:
    index = ast.parse(sources["index.py"])
    generation = _generation_stamp(index)
    inventory = {
        "schema_revision": 1,
        "generation": generation,
        "files": {name: sha256(source.encode("utf-8")).hexdigest() for name, source in sorted(sources.items())},
    }
    return json.dumps(inventory, sort_keys=True, indent=2) + "\n"


def _generation_stamp(tree: ast.Module) -> str:
    for statement in tree.body:
        if isinstance(statement, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == "GENERATION" for target in statement.targets
        ):
            value = ast.literal_eval(statement.value)
            if isinstance(value, str) and len(value) == 64:
                int(value, 16)
                return value
    raise ValueError("missing or invalid generation identity")


def _safe_relative_name(name: object) -> str:
    if not isinstance(name, str) or not name:
        raise ValueError("invalid relative artifact name")
    path = PurePosixPath(name)
    if path.is_absolute() or ".." in path.parts or path.as_posix() != name or "\\" in name:
        raise ValueError("invalid relative artifact name")
    return name


def validate_generation(root: Path) -> str:
    """Return the exact inventory identity, without importing generated code."""
    if root.is_symlink():
        raise ValueError("generated directory must not be a symlink")
    raw = (root / "inventory.json").read_bytes()
    inventory = json.loads(raw)
    if not isinstance(inventory, dict) or inventory.get("schema_revision") != 1 or not isinstance(inventory.get("files"), dict):
        raise ValueError("invalid generated inventory")
    files = inventory["files"]
    required = {"__init__.py", "index.py", "facade.py", "facade.pyi"}
    if not required.issubset(files) or "inventory.json" in files:
        raise ValueError("incomplete generated inventory")
    actual: set[str] = set()
    for path in root.rglob("*"):
        if path.is_symlink():
            raise ValueError("generated artifacts must not be symlinks")
        relative = path.relative_to(root)
        if "__pycache__" not in relative.parts and path.is_file() and path.name != "inventory.json":
            actual.add(relative.as_posix())
    if actual != set(files):
        raise ValueError("generated file inventory mismatch")
    trees: dict[str, ast.Module] = {}
    for name, expected_hash in files.items():
        _safe_relative_name(name)
        payload = (root / name).read_bytes()
        if sha256(payload).hexdigest() != expected_hash:
            raise ValueError(f"generated artifact hash mismatch: {name}")
        if name.endswith((".py", ".pyi")):
            trees[name] = ast.parse(payload.decode("utf-8"), filename=name)
    generation = _generation_stamp(trees["index.py"])
    if generation != inventory.get("generation"):
        raise ValueError("inventory generation mismatch")
    entries = next((statement.value for statement in trees["index.py"].body
                    if isinstance(statement, ast.Assign) and any(
                        isinstance(target, ast.Name) and target.id == "ENTRIES" for target in statement.targets
                    )), None)
    if not isinstance(entries, ast.Call) or len(entries.args) != 1 or not isinstance(entries.args[0], ast.Dict):
        raise ValueError("invalid generated index")
    modules: set[str] = set()
    for entry in entries.args[0].values:
        if not isinstance(entry, ast.Call) or not entry.args:
            raise ValueError("invalid generated index entry")
        module = ast.literal_eval(entry.args[0])
        if not isinstance(module, str) or not module.isidentifier():
            raise ValueError("invalid indexed group name")
        modules.add(module)
    for module in modules:
        name = f"{module}.py"
        if name not in trees or _generation_stamp(trees[name]) != generation:
            raise ValueError(f"missing or mixed generated group: {module}")
    return sha256(raw).hexdigest()


def require_admitted_generation(active: Path) -> str:
    marker = GenerationPublication(active).marker
    if marker.exists() or marker.is_symlink():
        raise RuntimeError("generated publication pending; recover before import or packaging")
    return validate_generation(active)


@dataclass(frozen=True, slots=True)
class GenerationPublication:
    active: Path

    @property
    def marker(self) -> Path:
        return self.active.parent / f".{self.active.name}.promotion.json"

    @property
    def backup(self) -> Path:
        return self.active.parent / f".{self.active.name}.backup"

    @property
    def rejected(self) -> Path:
        return self.active.parent / f".{self.active.name}.rejected"

    def promote(self, candidate: Path) -> None:
        """Promote only after successful generation, under exclusive offline access."""
        for path in (self.marker, self.backup, self.rejected):
            if path.exists() or path.is_symlink():
                raise FileExistsError(f"unexpected publication state: {path.name}")
        if candidate.parent.resolve() != self.active.parent.resolve() or candidate.name == self.active.name:
            raise ValueError("candidate must be a distinct same-filesystem sibling")
        if self.active.is_symlink():
            raise ValueError("active generation must not be a symlink")
        new_identity = validate_generation(candidate)
        old_identity = validate_generation(self.active) if self.active.exists() else None
        record = {"schema_revision": 1, "old_identity": old_identity, "candidate_identity": new_identity}
        with self.marker.open("x", encoding="utf-8") as stream:
            json.dump(record, stream, sort_keys=True)
        try:
            if old_identity is not None:
                self.active.rename(self.backup)
            candidate.rename(self.active)
            if validate_generation(self.active) != new_identity:
                raise ValueError("promoted inventory identity mismatch")
            self.marker.unlink()
        except Exception:
            self.recover()
            raise

    def recover(self) -> None:
        """Restore the verified old generation; repeated successful recovery is safe."""
        if self.marker.is_symlink():
            raise ValueError("invalid promotion marker; maintenance remains blocked")
        if not self.marker.exists():
            return
        record = json.loads(self.marker.read_bytes())
        if not isinstance(record, dict) or record.get("schema_revision") != 1 or "old_identity" not in record:
            raise ValueError("invalid promotion marker; maintenance remains blocked")
        old = record["old_identity"]
        for key in ("old_identity", "candidate_identity"):
            identity = record.get(key)
            if key == "old_identity" and identity is None:
                continue
            if not isinstance(identity, str) or len(identity) != 64 or any(
                character not in "0123456789abcdef" for character in identity
            ):
                raise ValueError("invalid promotion marker identity; maintenance remains blocked")
        if old is not None and self.active.exists():
            try:
                if validate_generation(self.active) == old:
                    self.marker.unlink()
                    return
            except (ValueError, OSError, SyntaxError):
                pass
        if old is not None and validate_generation(self.backup) != old:
            raise ValueError("backup inventory identity mismatch; maintenance remains blocked")
        if self.active.exists() or self.active.is_symlink():
            if self.active.is_symlink() or self.rejected.exists() or self.rejected.is_symlink():
                raise ValueError("unexpected recovery destination; maintenance remains blocked")
            self.active.rename(self.rejected)
        if old is not None:
            self.backup.rename(self.active)
            if validate_generation(self.active) != old:
                raise ValueError("restored inventory identity mismatch; maintenance remains blocked")
        self.marker.unlink()

    def cleanup_backup(self, expected_identity: str) -> None:
        require_admitted_generation(self.active)
        if not self.backup.exists():
            return
        if validate_generation(self.backup) != expected_identity:
            raise ValueError("backup cleanup identity mismatch")
        shutil.rmtree(self.backup)

    def cleanup_rejected(self, expected_identity: str) -> None:
        """Remove a verified quarantined candidate only after recovery finishes."""
        if self.marker.exists() or self.marker.is_symlink():
            raise RuntimeError("generated publication pending; recover before cleanup")
        if not self.rejected.exists() and not self.rejected.is_symlink():
            return
        if validate_generation(self.rejected) != expected_identity:
            raise ValueError("rejected cleanup identity mismatch")
        shutil.rmtree(self.rejected)
