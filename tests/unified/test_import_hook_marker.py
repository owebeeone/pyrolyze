"""Unit checks for import-hook eligibility (no ``#@pyrolyze`` in this file)."""

from __future__ import annotations

from pyrolyze.compiler import import_hook


def test_pyrolyze_marker_only_first_two_lines() -> None:
    assert import_hook._raw_source_has_pyrolyze_marker("#@pyrolyze\nimport m\n")
    assert not import_hook._raw_source_has_pyrolyze_marker(
        "import m\nimport n\n#@pyrolyze\n",
    )


def test_install_registers_at_most_once() -> None:
    import sys

    from pyrolyze.compiler.import_hook import PyrolyzeMetaPathFinder, install, uninstall

    uninstall()
    install()
    assert sum(1 for f in sys.meta_path if isinstance(f, PyrolyzeMetaPathFinder)) == 1
    install()
    assert sum(1 for f in sys.meta_path if isinstance(f, PyrolyzeMetaPathFinder)) == 1
