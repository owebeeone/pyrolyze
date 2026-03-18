from __future__ import annotations

from pathlib import Path
import textwrap

import pytest

from pyrolyze.compiler import emit_transformed_source


_GOLDENS_DIR = Path(__file__).parent / "v3_14" / "goldens"


_CASES: dict[str, tuple[str, str, str]] = {
    "phase3_greeting.py": (
        """
from pyrolyze.api import pyrolyse, pyrolyze_slotted

@pyrolyze_slotted
def format_title(name):
    return f"Hello {name}"

def record(value):
    return value

@pyrolyse
def greeting(name):
    title = format_title(name)
    label = title + "!"
    record(label)
""",
        "golden.phase3.greeting",
        "/virtual/goldens/phase3_greeting.py",
    ),
    "phase4_stats_panel.py": (
        """
from contextlib import contextmanager

from pyrolyze.api import pyrolyse

log = []

@contextmanager
def section(title, *, accent):
    log.append(("section.enter", title, accent))
    try:
        yield
    finally:
        log.append(("section.exit", title, accent))

def badge(text, *, tone):
    log.append(("badge", text, tone))

@pyrolyse
def stats_panel(show_extra, count):
    with section("Stats", accent="green"):
        badge(f"Count: {count}", tone="info")
        if show_extra:
            badge("Visible", tone="success")
        else:
            badge("Hidden", tone="muted")
""",
        "golden.phase4.stats_panel",
        "/virtual/goldens/phase4_stats_panel.py",
    ),
    "phase5_parent_panel.py": (
        """
from pyrolyze.api import pyrolyse

log = []

def badge(text, *, tone):
    log.append(("badge", text, tone))

@pyrolyse
def child_badge(text):
    badge(text, tone="info")

@pyrolyse
def parent_panel(text):
    child_badge(text)
""",
        "golden.phase5.parent_panel",
        "/virtual/goldens/phase5_parent_panel.py",
    ),
    "phase7_label_panel.py": (
        """
from pyrolyze.api import Label, call_native, pyrolyse

@pyrolyse
def label_panel(text):
    call_native(Label)(text=text)
""",
        "golden.phase7.label_panel",
        "/virtual/goldens/phase7_label_panel.py",
    ),
}


@pytest.mark.parametrize(
    ("golden_name", "source", "module_name", "filename"),
    [
        (golden_name, source, module_name, filename)
        for golden_name, (source, module_name, filename) in _CASES.items()
    ],
)
def test_transformed_source_matches_v3_14_golden(
    golden_name: str,
    source: str,
    module_name: str,
    filename: str,
) -> None:
    transformed = emit_transformed_source(
        textwrap.dedent(source),
        module_name=module_name,
        filename=filename,
    )

    expected = _read_golden(_GOLDENS_DIR / golden_name)
    assert transformed == expected


def _read_golden(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    return text[:-1] if text.endswith("\n") else text
