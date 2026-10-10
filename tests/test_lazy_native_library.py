from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from collections.abc import Iterator
import importlib
import inspect
from pathlib import Path
import sys

import pytest

from pyrolyze.compiler import load_transformed_namespace
from pyrolyze.import_hook import PyRolyzeFinder
from pyrolyze.runtime import RenderContext, dirtyof
from pyrolyze_tools.generate_grouped_native_library import write_grouped_library
from pyrolyze_tools.generate_semantic_library import DiscoveredWidgetClass


@pytest.fixture
def lazy_package(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[tuple[str, Path]]:
    package = "lazy_group_fixture"
    widgets = tuple(DiscoveredWidgetClass("builtins", name, f"C{name}", ())
                    for name in ("Button", "Label", "Row"))
    write_grouped_library(
        "builtins", widgets, families={"CButton": "controls", "CLabel": "controls", "CRow": "layouts"},
        maximum_kinds=2, output_dir=tmp_path / package,
    )
    monkeypatch.syspath_prepend(str(tmp_path))
    monkeypatch.setattr(sys, "meta_path", [PyRolyzeFinder(), *sys.meta_path])
    yield package, tmp_path / package
    for name in tuple(sys.modules):
        if name == package or name.startswith(package + "."):
            sys.modules.pop(name, None)


def test_facade_preserves_binding_and_loads_only_requested_group(lazy_package: tuple[str, Path]) -> None:
    package, _ = lazy_package
    index = importlib.import_module(f"{package}.index")
    facade = importlib.import_module(f"{package}.facade").BuiltinsUiLibrary
    assert tuple(facade.WIDGET_SPECS) == tuple(index.ENTRIES)
    assert "CButton" in dir(facade)
    assert "Button" in facade.WIDGET_SPECS
    assert all(f"{package}.{entry.module_name}" not in sys.modules for entry in index.ENTRIES.values())
    with ThreadPoolExecutor(max_workers=4) as executor:
        results = list(executor.map(lambda i: getattr(facade, "CButton" if i % 2 == 0 else "CLabel"), range(12)))
    callback = results[0]
    assert all(result is (facade.CButton if i % 2 == 0 else facade.CLabel) for i, result in enumerate(results))
    assert callback is facade.CButton
    assert callback.__self__ is facade
    assert tuple(inspect.signature(callback).parameters) == ()
    assert callback._pyrolyze_meta is not None
    assert facade.WIDGET_SPECS["Button"] is facade.WIDGET_SPECS["Button"]
    assert f"{package}.{index.ENTRIES['Row'].module_name}" not in sys.modules
    with pytest.raises(AttributeError):
        _ = facade.CUnknown
    with pytest.raises(KeyError):
        _ = facade.WIDGET_SPECS["Unknown"]
    assert facade.WIDGET_SPECS.get("Unknown") is None
    assert facade().CButton is facade.CButton
    assert facade().CRow.__self__ is facade
    derived = type("DerivedLibrary", (facade,), {})
    assert derived.CButton.__self__ is derived
    assert derived.CButton is derived.CButton
    assert derived.CButton.__func__ is facade.CButton.__func__
    assert derived.CRow.__self__ is derived
    namespace = load_transformed_namespace(
        f"from {package}.facade import BuiltinsUiLibrary as Widgets\n"
        "from pyrolyze.api import pyrolyze\n"
        "@pyrolyze\ndef panel() -> None:\n    Widgets.CButton()\n",
        module_name="lazy_facade_panel",
    )
    context = RenderContext()
    try:
        namespace["panel"]._pyrolyze_meta._func(context, dirtyof())
        assert tuple(element.kind for element in context.committed_ui()) == ("Button",)
    finally:
        context.close_app_contexts()


@pytest.mark.parametrize("fault_source", (
    'BuiltinsUiLibrary.WIDGET_SPECS = {"Button": BuiltinsUiLibrary.WIDGET_SPECS["Button"]}',
    'GENERATION = "incorrect-generation"',
))
def test_invalid_sibling_prevents_any_group_publication(
    lazy_package: tuple[str, Path], fault_source: str
) -> None:
    package, root = lazy_package
    index = importlib.import_module(f"{package}.index")
    entry = index.ENTRIES["Label"]
    path = root / f"{entry.module_name}.py"
    with path.open("a") as stream:
        stream.write(f"\n{fault_source}\n")
    facade = importlib.import_module(f"{package}.facade").BuiltinsUiLibrary
    def resolve_failure(name: str) -> str:
        with pytest.raises(RuntimeError, match="group") as error:
            getattr(facade, name)
        return str(error.value).split("; requested=")[0]

    with ThreadPoolExecutor(max_workers=4) as executor:
        messages = list(executor.map(resolve_failure, ("CButton", "CLabel") * 4))
    assert len(set(messages)) == 1
    for name in ("CButton", "CLabel", "CButton"):
        with pytest.raises(RuntimeError, match="group"):
            getattr(facade, name)
        assert "CButton" not in vars(facade)
        assert "CLabel" not in vars(facade)
    assert facade.CRow.__self__ is facade
    with pytest.raises(RuntimeError, match="group"):
        facade.WIDGET_SPECS.get("Button")


def test_suppressed_reentry_still_prevents_publication(lazy_package: tuple[str, Path]) -> None:
    package, root = lazy_package
    index = importlib.import_module(f"{package}.index")
    path = root / f"{index.ENTRIES['Button'].module_name}.py"
    with path.open("a") as stream:
        stream.write(
            '\nFacade = __import__(__package__ + ".facade", fromlist=("BuiltinsUiLibrary",)).BuiltinsUiLibrary\n'
            "try:\n    Facade.CButton\nexcept RuntimeError:\n    pass\n"
        )
    facade = importlib.import_module(f"{package}.facade").BuiltinsUiLibrary
    with pytest.raises(RuntimeError, match="reentrant"):
        _ = facade.CButton
    assert facade.CRow.__self__ is facade
