from __future__ import annotations

import inspect
from typing import get_args, get_origin

import pytest

from pyrolyze.api import (
    CallFromNonPyrolyzeContext,
    ComponentMetadata,
    ComponentRef,
    pyrolyze_component_ref,
)


def _runtime_neutral_badge(ctx: object, text: object) -> None:
    del ctx, text


def test_component_ref_decorator_attaches_metadata_and_preserves_function_object() -> None:
    def neutral_badge(text: str) -> None:
        raise CallFromNonPyrolyzeContext("neutral_badge")

    decorated = pyrolyze_component_ref(
        ComponentMetadata("neutral_badge", _runtime_neutral_badge)
    )(neutral_badge)

    assert decorated is neutral_badge
    assert decorated.__name__ == "neutral_badge"
    signature = inspect.signature(decorated)
    assert tuple(signature.parameters) == ("text",)
    assert signature.parameters["text"].annotation == "str"
    assert signature.return_annotation == "None"

    meta = decorated._pyrolyze_meta
    assert meta.name == "neutral_badge"
    assert meta._func is _runtime_neutral_badge


def test_component_ref_direct_call_raises_plain_python_exception() -> None:
    @pyrolyze_component_ref(ComponentMetadata("neutral_badge", _runtime_neutral_badge))
    def neutral_badge(text: str) -> None:
        raise CallFromNonPyrolyzeContext("neutral_badge")

    with pytest.raises(CallFromNonPyrolyzeContext, match="neutral_badge"):
        neutral_badge("hello")


def test_component_ref_typing_surface_is_callable_shaped() -> None:
    @pyrolyze_component_ref(ComponentMetadata("neutral_badge", _runtime_neutral_badge))
    def neutral_badge(text: str) -> None:
        raise CallFromNonPyrolyzeContext("neutral_badge")

    alias = ComponentRef[[str]]
    assert get_origin(alias) is ComponentRef
    assert get_args(alias) == ((str,),)

    chosen: ComponentRef[[str]] = neutral_badge
    assert chosen._pyrolyze_meta._func is _runtime_neutral_badge
