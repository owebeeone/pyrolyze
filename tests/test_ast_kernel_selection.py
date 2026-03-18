from __future__ import annotations

from types import SimpleNamespace

from pyrolyze.compiler import kernel_loader


def test_select_kernel_version_prefers_exact_python_match() -> None:
    selected = kernel_loader.select_kernel_version(
        (3, 14),
        available_versions=[(3, 12), (3, 14)],
    )

    assert selected == (3, 14)


def test_select_kernel_version_falls_back_to_latest_available() -> None:
    selected = kernel_loader.select_kernel_version(
        (3, 99),
        available_versions=[(3, 12), (3, 14)],
    )

    assert selected == (3, 14)


def test_load_ast_kernel_imports_only_selected_version(monkeypatch) -> None:
    imported: list[str] = []
    sentinel = object()

    monkeypatch.setattr(
        kernel_loader,
        "_available_kernel_versions",
        lambda: [(3, 12), (3, 14)],
    )
    monkeypatch.setattr(
        kernel_loader,
        "sys",
        SimpleNamespace(version_info=SimpleNamespace(major=3, minor=99)),
    )

    def fake_import(name: str):
        imported.append(name)
        return sentinel

    monkeypatch.setattr(kernel_loader.importlib, "import_module", fake_import)

    loaded = kernel_loader.load_ast_kernel()

    assert loaded is sentinel
    assert imported == ["pyrolyze.compiler.kernels.v3_14.kernel"]
