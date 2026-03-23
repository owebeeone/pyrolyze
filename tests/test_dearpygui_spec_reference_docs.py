"""Tests for spec-driven Dear PyGui reference Markdown generation."""

from __future__ import annotations

from pathlib import Path

from frozendict import frozendict

from pyrolyze.backends.model import (
    AccessorKind,
    ChildPolicy,
    PropMode,
    TypeRef,
    UiParamSpec,
    UiPropSpec,
    UiWidgetSpec,
)

from pyrolyze_tools.dearpygui_spec_reference_docs import write_dearpygui_reference_docs


def test_write_dearpygui_reference_docs_minimal_spec(tmp_path: Path) -> None:
    specs = frozendict(
        {
            "DpgTestItem": UiWidgetSpec(
                kind="DpgTestItem",
                mounted_type_name="test.M_add_test",
                constructor_params=frozendict(
                    {
                        "label": UiParamSpec(
                            name="label",
                            annotation=TypeRef("str"),
                            default_repr="None",
                        ),
                    }
                ),
                props=frozendict(
                    {
                        "width": UiPropSpec(
                            name="width",
                            annotation=TypeRef("int"),
                            mode=PropMode.CREATE_UPDATE,
                            constructor_name="width",
                            setter_kind=AccessorKind.DPG_CONFIG,
                            setter_name="width",
                        ),
                    }
                ),
                methods=frozendict(),
                child_policy=ChildPolicy.NONE,
            ),
        }
    )
    ent_path, prop_path = write_dearpygui_reference_docs(tmp_path, specs=specs)
    assert ent_path.exists() and prop_path.exists()
    entities = ent_path.read_text(encoding="utf-8")
    properties = prop_path.read_text(encoding="utf-8")
    assert "DpgTestItem" in entities
    assert "entity-dpgtestitem" in entities
    assert "Dear PyGui generated library" in entities
    assert "dpg.configure(item, width=...)" in entities
    assert "`label`" in entities
    assert "dpg.configure" in properties
    assert "prop-label" in properties
