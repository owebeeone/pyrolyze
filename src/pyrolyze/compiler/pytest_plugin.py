"""Pytest plugin: enable ``#@pyrolyze`` on-disk modules during collection and tests.

Runs in ``pytest_configure`` (after pytest installs its assertion rewrite hook) and
calls :func:`pyrolyze.compiler.import_hook.install`, which moves the PyRolyze finder
to ``sys.meta_path[0]`` so compilation wins over assert rewriting.
"""

from __future__ import annotations


def pytest_configure() -> None:
    from pyrolyze.compiler.import_hook import install

    install()
