"""Ensure the ``#@pyrolyze`` meta-path hook is registered when the package loads.

Backend modules such as ``generated_library.py`` are checked in as plain
``#@pyrolyze`` source. :mod:`pyrolyze.import_hook` must run before their
``exec_module`` so ``@pyrolyze`` is compiled. If the hook is absent, authors still
import :func:`pyrolyze.api.pyrolyze`, which is intentionally a stub that raises.

A venv can still use ``pyrolyze-import-hook-pth install`` so the hook is present
before any ``pyrolyze`` import (see ``pyrolyze.import_hook.install_startup_import_hook``).
For normal ``python app.py`` runs without that ``.pth``, importing any
``pyrolyze.*`` submodule loads this package first, so calling
:func:`install_compiler_import_hook` here fixes ordering without a second process
or a ``runpy`` restart.

**Note:** A ``runpy``/``SystemExit`` restart from :mod:`pyrolyze.__init__` is unsafe:
``site`` may still be executing ``.pth`` lines (for example
``import pyrolyze.import_hook``), and raising :exc:`SystemExit` during that phase
fails interpreter startup.
"""

from __future__ import annotations

import sys


def apply() -> None:
    """Register :class:`~pyrolyze.import_hook.PyrolyzeMetaPathFinder` if missing."""

    from .import_hook import (
        PyrolyzeMetaPathFinder,
        install_startup_import_hook,
    )

    if any(isinstance(h, PyrolyzeMetaPathFinder) for h in sys.meta_path):
        return

    install_startup_import_hook()


__all__ = ["apply"]
