"""Pytest plugin: enable ``#@pyrolyze`` on-disk modules during collection and tests.

Runs in ``pytest_configure`` (after pytest installs its assertion rewrite hook) and
calls :func:`pyrolyze.import_hook.install_startup_import_hook`, which moves the PyRolyze finder
to ``sys.meta_path[0]`` so compilation wins over assert rewriting.
"""

from __future__ import annotations


def pytest_configure() -> None:
    from pyrolyze.import_hook import install_startup_import_hook

    install_startup_import_hook()
