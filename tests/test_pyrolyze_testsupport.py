from __future__ import annotations

from contextlib import contextmanager
import inspect

from pyrolyze_testsupport import pyrolize_test_native, pyrolize_test_wrap


def test_pyrolize_test_wrap_preserves_public_signature_and_attaches_runtime_metadata() -> None:
    calls: list[tuple[object, ...]] = []

    @pyrolize_test_wrap
    def badge(text: str, *, tone: str = "info") -> None:
        calls.append((text, tone))

    signature = inspect.signature(badge)
    assert tuple(signature.parameters) == ("text", "tone")
    assert signature.parameters["text"].annotation == "str"
    assert signature.parameters["tone"].annotation == "str"
    assert signature.return_annotation == "None"

    meta = badge._pyrolyze_meta
    assert meta.name == "badge"

    meta._func(object(), object(), "Hello", tone="warn")
    badge("Direct")
    assert calls == [("Hello", "warn"), ("Direct", "info")]


def test_pyrolize_test_native_preserves_signature_and_forwards_runtime_context() -> None:
    calls: list[tuple[object, ...]] = []

    class _FakeCtx:
        @contextmanager
        def pass_scope(self):
            yield self

    @pyrolize_test_native
    def badge(ctx: object, text: str, *, tone: str = "info") -> None:
        calls.append((ctx, text, tone))

    signature = inspect.signature(badge)
    assert tuple(signature.parameters) == ("ctx", "text", "tone")
    assert signature.parameters["ctx"].annotation == "object"
    assert signature.parameters["text"].annotation == "str"
    assert signature.parameters["tone"].annotation == "str"
    assert signature.return_annotation == "None"

    meta = badge._pyrolyze_meta
    assert meta.name == "badge"

    ctx = _FakeCtx()
    meta._func(ctx, object(), "Hello", tone="warn")
    badge(ctx, "Direct")
    assert calls == [(ctx, "Hello", "warn"), (ctx, "Direct", "info")]
