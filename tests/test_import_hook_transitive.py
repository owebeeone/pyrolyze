from __future__ import annotations

import importlib
import sys
from pathlib import Path

from pyrolyze.import_hook import install_import_hook, uninstall_import_hook
from pyrolyze.pyrolyze_tools.import_hook_pth import PTH_LINE


def test_import_hook_transforms_transitively_imported_pyrolyze_modules(
    tmp_path: Path,
    monkeypatch,
) -> None:
    package_dir = tmp_path / "demoapp"
    package_dir.mkdir()
    (package_dir / "__init__.py").write_text("", encoding="utf-8")
    (package_dir / "child.py").write_text(
        "#@pyrolyze\n"
        "from pyrolyze.api import pyrolyze\n"
        "\n"
        "@pyrolyze\n"
        "def child_panel() -> None:\n"
        "    pass\n",
        encoding="utf-8",
    )
    (package_dir / "root.py").write_text(
        "#@pyrolyze\n"
        "from pyrolyze.api import pyrolyze\n"
        "from demoapp.child import child_panel\n"
        "\n"
        "@pyrolyze\n"
        "def root_panel() -> None:\n"
        "    child_panel()\n",
        encoding="utf-8",
    )

    monkeypatch.syspath_prepend(str(tmp_path))
    monkeypatch.setenv("PYROLYZE_ENABLE_IMPORT_HOOK", "1")

    uninstall_import_hook()
    sys.modules.pop("demoapp.root", None)
    sys.modules.pop("demoapp.child", None)
    sys.modules.pop("demoapp", None)

    try:
        finder = install_import_hook()
        assert finder is not None

        root = importlib.import_module("demoapp.root")
        child = importlib.import_module("demoapp.child")

        assert hasattr(root.root_panel, "_pyrolyze_meta")
        assert hasattr(child.child_panel, "_pyrolyze_meta")
        assert hasattr(root, "__pyrolyze_artifact__")
        assert hasattr(child, "__pyrolyze_artifact__")
    finally:
        uninstall_import_hook()
        sys.modules.pop("demoapp.root", None)
        sys.modules.pop("demoapp.child", None)
        sys.modules.pop("demoapp", None)


def test_pth_bootstrap_uses_public_import_hook_entrypoint() -> None:
    assert (
        PTH_LINE
        == "import pyrolyze.import_hook; pyrolyze.import_hook.install_startup_import_hook()\n"
    )
