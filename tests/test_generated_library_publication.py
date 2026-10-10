from __future__ import annotations

from pathlib import Path
import json

import pytest

from pyrolyze_tools.generate_grouped_native_library import write_grouped_library
from pyrolyze_tools.generate_semantic_library import DiscoveredWidgetClass
from pyrolyze_tools.generated_library_publication import (
    GenerationPublication,
    require_admitted_generation,
    validate_generation,
)


def _generate(path: Path, name: str) -> str:
    widget = DiscoveredWidgetClass("builtins", name, f"C{name}", ())
    write_grouped_library("builtins", (widget,), families={widget.public_name: "controls"},
                          maximum_kinds=1, output_dir=path)
    return validate_generation(path)


def test_complete_directory_promotion_retains_old_generation(tmp_path: Path) -> None:
    active = tmp_path / "_generated"
    candidate = tmp_path / "candidate"
    old = _generate(active, "Button")
    new = _generate(candidate, "Label")
    publication = GenerationPublication(active)
    publication.promote(candidate)
    assert require_admitted_generation(active) == new
    assert validate_generation(publication.backup) == old
    assert not publication.marker.exists()
    with pytest.raises(FileExistsError):
        publication.promote(tmp_path / "another")
    publication.cleanup_backup(old)
    assert not publication.backup.exists()


@pytest.mark.parametrize("has_old", (False, True))
def test_interrupted_promotion_recovers_before_admission(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, has_old: bool
) -> None:
    active = tmp_path / "_generated"
    candidate = tmp_path / "candidate"
    old = _generate(active, "Button") if has_old else None
    _generate(candidate, "Label")
    publication = GenerationPublication(active)
    rename = Path.rename

    def interrupt(self: Path, target: Path) -> Path:
        if self == candidate:
            raise KeyboardInterrupt("interrupted before candidate install")
        return rename(self, target)

    with monkeypatch.context() as patch:
        patch.setattr(Path, "rename", interrupt)
        with pytest.raises(KeyboardInterrupt):
            publication.promote(candidate)
    assert publication.marker.exists()
    with pytest.raises(RuntimeError, match="pending"):
        require_admitted_generation(active)
    publication.recover()
    publication.recover()
    assert not publication.marker.exists()
    if has_old:
        assert require_admitted_generation(active) == old
    else:
        assert not active.exists()
        with pytest.raises((FileNotFoundError, ValueError)):
            require_admitted_generation(active)
    publication.promote(candidate)
    assert active.exists()


def test_failed_restoration_stays_pending_until_retry(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    active = tmp_path / "_generated"
    candidate = tmp_path / "candidate"
    old = _generate(active, "Button")
    _generate(candidate, "Label")
    publication = GenerationPublication(active)
    rename = Path.rename

    def fail(self: Path, target: Path) -> Path:
        if self == candidate:
            raise KeyboardInterrupt("before installation")
        if self == publication.backup:
            raise OSError("restoration unavailable")
        return rename(self, target)

    with monkeypatch.context() as patch:
        patch.setattr(Path, "rename", fail)
        with pytest.raises(KeyboardInterrupt):
            publication.promote(candidate)
        with pytest.raises(OSError, match="restoration"):
            publication.recover()
    assert publication.marker.exists()
    assert validate_generation(publication.backup) == old
    with pytest.raises(RuntimeError, match="pending"):
        require_admitted_generation(active)
    publication.recover()
    assert require_admitted_generation(active) == old


def test_failed_backup_cleanup_does_not_revoke_admission(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    active = tmp_path / "_generated"
    candidate = tmp_path / "candidate"
    old = _generate(active, "Button")
    new = _generate(candidate, "Label")
    publication = GenerationPublication(active)
    publication.promote(candidate)

    def fail(path: Path) -> None:
        raise OSError("cleanup unavailable")

    monkeypatch.setattr("pyrolyze_tools.generated_library_publication.shutil.rmtree", fail)
    with pytest.raises(OSError, match="cleanup"):
        publication.cleanup_backup(old)
    assert require_admitted_generation(active) == new
    assert validate_generation(publication.backup) == old


@pytest.mark.parametrize("damage", ("missing", "modified", "extra"))
def test_incomplete_or_mixed_generation_is_rejected(tmp_path: Path, damage: str) -> None:
    active = tmp_path / "_generated"
    _generate(active, "Button")
    path = active / "facade.py"
    if damage == "missing":
        path.unlink()
    elif damage == "modified":
        path.write_text(path.read_text() + "\nunexpected = True\n")
    else:
        (active / "stale.py").write_text("stale = True\n")
    with pytest.raises(ValueError):
        require_admitted_generation(active)


def test_error_during_promotion_restores_old_directory(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    active = tmp_path / "_generated"
    candidate = tmp_path / "candidate"
    old = _generate(active, "Button")
    _generate(candidate, "Label")
    publication = GenerationPublication(active)
    rename = Path.rename

    def fail(self: Path, target: Path) -> Path:
        if self == candidate:
            raise OSError("candidate rename failed")
        return rename(self, target)

    monkeypatch.setattr(Path, "rename", fail)
    with pytest.raises(OSError):
        publication.promote(candidate)
    assert require_admitted_generation(active) == old
    assert not publication.marker.exists()


@pytest.mark.parametrize("candidate_identity", (None, "", "z" * 64))
def test_invalid_marker_preserves_active_generation(tmp_path: Path, candidate_identity: str | None) -> None:
    active = tmp_path / "_generated"
    old = _generate(active, "Button")
    publication = GenerationPublication(active)
    record = {"schema_revision": 1, "old_identity": None}
    if candidate_identity is not None:
        record["candidate_identity"] = candidate_identity
    publication.marker.write_text(json.dumps(record))
    with pytest.raises(ValueError, match="marker"):
        publication.recover()
    assert validate_generation(active) == old
    assert publication.marker.exists()


@pytest.mark.parametrize("has_old", (False, True))
def test_interruption_after_install_quarantines_candidate(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, has_old: bool
) -> None:
    active = tmp_path / "_generated"
    candidate = tmp_path / "candidate"
    old = _generate(active, "Button") if has_old else None
    new = _generate(candidate, "Label")
    publication = GenerationPublication(active)
    unlink = Path.unlink

    def interrupt(self: Path, *args: object, **kwargs: object) -> None:
        if self == publication.marker:
            raise KeyboardInterrupt("installed but not admitted")
        unlink(self, *args, **kwargs)

    with monkeypatch.context() as patch:
        patch.setattr(Path, "unlink", interrupt)
        with pytest.raises(KeyboardInterrupt):
            publication.promote(candidate)
    with pytest.raises(RuntimeError, match="pending"):
        require_admitted_generation(active)
    publication.recover()
    assert validate_generation(publication.rejected) == new
    assert not publication.marker.exists()
    if has_old:
        assert require_admitted_generation(active) == old
    else:
        assert not active.exists()
    with pytest.raises(ValueError, match="identity"):
        publication.cleanup_rejected("0" * 64)
    publication.cleanup_rejected(new)
    assert not publication.rejected.exists()
    retry = tmp_path / "retry"
    _generate(retry, "Label")
    publication.promote(retry)
    assert require_admitted_generation(active) == new
