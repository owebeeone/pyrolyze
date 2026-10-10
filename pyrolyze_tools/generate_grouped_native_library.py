"""Emit separately importable native definition groups into fresh staging."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from hashlib import sha256
import json
from pathlib import Path

from pyrolyze_tools.generate_semantic_library import (
    DiscoveredWidgetClass,
    _assign_kind_names,
    _generate_library_source,
    _library_class_name,
    _render_mount_selectors,
    _render_ui_interface_entries,
    _public_parameters_for_widget,
    _render_signature_lines,
)
from pyrolyze_tools.native_library_grouping import group_widget_kinds
from pyrolyze_tools.generated_library_publication import generation_inventory_source, validate_generation


def generate_grouped_library_sources(
    root_module_name: str,
    widgets: Sequence[DiscoveredWidgetClass],
    *,
    families: Mapping[str, str],
    maximum_kinds: int,
    accepted_source: str | None = None,
) -> dict[str, str]:
    """Families are explicit public-name assignments; names are catalog-wide."""
    kind_names = _assign_kind_names(root_module_name, widgets)
    by_kind: dict[str, DiscoveredWidgetClass] = {}
    public_names: set[str] = set()
    for widget in widgets:
        kind = kind_names[widget.module_name, widget.class_name]
        if kind in by_kind or widget.public_name in public_names:
            raise ValueError("duplicate widget kind or public name")
        by_kind[kind] = widget
        public_names.add(widget.public_name)
    if set(families) != public_names:
        raise ValueError("families must assign every public name exactly once")
    groups = group_widget_kinds(
        {kind: families[widget.public_name] for kind, widget in by_kind.items()},
        maximum_kinds=maximum_kinds,
    )
    sources = {
        f"{group.module_name}.py": _generate_library_source(
            root_module_name, tuple(by_kind[kind] for kind in group.kinds), kind_names
        )
        for group in groups
    }
    class_name = _library_class_name(root_module_name.split(".", 1)[0])
    ordered_widgets = tuple(by_kind[kind] for kind in sorted(by_kind))
    facade = [
        '"""Generated lazy native facade; definitions load by indexed group."""',
        "from __future__ import annotations",
        "from typing import Any, ClassVar",
        "from collections.abc import Mapping",
        "from frozendict import frozendict",
        "from pyrolyze.api import MountSelector, UIElement, ui_interface",
        "from pyrolyze.backends.model import UiInterface, UiInterfaceEntry, UiWidgetSpec",
        "from pyrolyze.backends.lazy_library import LazyLibraryCatalog, LazyUiLibraryMeta",
        "from .index import ENTRIES, GENERATION",
        "from pyrolyze.backends.generated_package import admit_generated_package",
        "admit_generated_package(__file__, GENERATION)",
        "",
        "@ui_interface",
        f"class {class_name}(metaclass=LazyUiLibraryMeta):",
        f"    ROOT_MODULE: ClassVar[str] = {root_module_name!r}",
        "    _lazy_catalog = LazyLibraryCatalog(__package__, GENERATION, ENTRIES)",
        "    def __getattr__(self, name: str) -> Any:",
        "        return getattr(type(self), name)",
        "    WIDGET_SPECS: ClassVar[Mapping[str, UiWidgetSpec]] = _lazy_catalog",
        f"    UI_INTERFACE = UiInterface(name={class_name!r}, owner=None, entries=frozendict({{",
        *_render_ui_interface_entries(ordered_widgets, kind_names),
        "    }))",
        *_render_mount_selectors(ordered_widgets),
        "",
        "    @classmethod",
        "    def __element(cls, *, kind: str, kwds: dict[str, Any]) -> UIElement:",
        "        return UIElement(kind=kind, props=dict(kwds))",
        "",
    ]
    sources["facade.py"] = "\n".join(facade)
    stub = [
        "from typing import Any, ClassVar",
        "from collections.abc import Mapping",
        "from pyrolyze.api import MISSING, MissingType, MountSelector, PyrolyzeHandler",
        "from pyrolyze.backends.model import UiInterface, UiWidgetSpec",
        f"import {root_module_name.split('.', 1)[0]}",
        "",
        f"class {class_name}:",
        "    ROOT_MODULE: ClassVar[str]",
        "    UI_INTERFACE: ClassVar[UiInterface]",
        "    WIDGET_SPECS: ClassVar[Mapping[str, UiWidgetSpec]]",
        *_render_mount_selectors(ordered_widgets),
    ]
    for widget in ordered_widgets:
        stub.extend([
            "",
            "    @classmethod",
            f"    def {widget.public_name}(",
            *_render_signature_lines(_public_parameters_for_widget(root_module_name.split('.', 1)[0], widget)),
            "    ) -> None: ...",
        ])
    sources["facade.pyi"] = "\n".join(stub) + "\n"
    sources["__init__.py"] = (
        '"""Generated definitions; resolve groups explicitly."""\n'
        "from pyrolyze.backends.generated_package import admit_generated_package\n"
        "admit_generated_package(__file__)\n"
    )
    if accepted_source is not None:
        from pyrolyze_tools.preserve_native_catalog import preserve_catalog

        sources = preserve_catalog(sources, accepted_source)
    configuration = {
        "root_module": root_module_name,
        "maximum_kinds": maximum_kinds,
        "families": dict(sorted(families.items())),
        "schema_revision": 1,
    }
    generation = sha256(json.dumps(
        {"configuration": configuration, "sources": sources}, sort_keys=True
    ).encode("utf-8")).hexdigest()
    for group in groups:
        sources[f"{group.module_name}.py"] += f"\nGENERATION = {generation!r}\n"

    index = [
        '"""Generated name-only inventory; importing it never imports shards."""',
        "from dataclasses import dataclass",
        "from types import MappingProxyType",
        "",
        "@dataclass(frozen=True, slots=True)",
        "class DefinitionEntry:",
        "    module_name: str",
        "    class_name: str",
        "    public_name: str",
        "    family: str",
        "",
        f"GENERATION = {generation!r}",
        f"MAXIMUM_KINDS = {maximum_kinds!r}",
        f"ROOT_MODULE = {root_module_name!r}",
        "ENTRIES = MappingProxyType({",
    ]
    for group in groups:
        for kind in group.kinds:
            index.append(
                f"    {kind!r}: DefinitionEntry({group.module_name!r}, {class_name!r}, "
                f"{by_kind[kind].public_name!r}, {group.family!r}),"
            )
    index.extend(["})", ""])
    sources["index.py"] = "\n".join(index)
    sources["inventory.json"] = generation_inventory_source(sources)
    return sources


def write_grouped_library(
    root_module_name: str,
    widgets: Sequence[DiscoveredWidgetClass],
    *,
    families: Mapping[str, str],
    maximum_kinds: int,
    output_dir: Path,
    accepted_source: str | None = None,
) -> tuple[Path, ...]:
    """Create a new staging package, never replace an existing output tree."""
    sources = generate_grouped_library_sources(
        root_module_name, widgets, families=families, maximum_kinds=maximum_kinds,
        accepted_source=accepted_source,
    )
    output_dir.mkdir(parents=True, exist_ok=False)
    paths: list[Path] = []
    for name, source in sorted(sources.items()):
        if name == "inventory.json":
            continue
        path = output_dir / name
        path.write_text(source, encoding="utf-8")
        paths.append(path)
    inventory = output_dir / "inventory.json"
    inventory.write_text(sources["inventory.json"], encoding="utf-8")
    paths.append(inventory)
    validate_generation(output_dir)
    return tuple(paths)
