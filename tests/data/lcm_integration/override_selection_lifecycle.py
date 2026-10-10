"""Lexical overrides publish stable streams only after outer acceptance."""

from __future__ import annotations

import json
from typing import Any

from pyrolyze.runtime import context_lifecycle as runtime
from pyrolyze.runtime.app_context import AppContextKey


def characterize() -> dict[str, Any]:
    root = runtime.RenderContext()
    key = AppContextKey("theme", lambda host: "unused")
    module = runtime.ModuleId("override-proof")
    outer_id, inner_id = runtime.SlotId(module, 1), runtime.SlotId(module, 2)
    result: dict[str, Any] = {}
    with root.pass_scope():
        with root.open_app_context_override(outer_id, (key,), "old") as outer:
            parent_ref = outer.authored_app_context_ref(key)
            with outer.open_app_context_override(inner_id, (key,), None) as inner:
                ref = inner.authored_app_context_ref(key)
                result["lexical"] = [inner.get_authored_app_context(key), ref.get()]
    observations = []

    def changed() -> None:
        tracker = root.get_app_context(
            root._generation_tracker_key
        )
        observations.append(
            [
                ref.get(),
                tracker.committed_generation_id,
                tracker.active_generation_id is None,
                root.debug_is_active(outer_id),
            ]
        )

    unsubscribe = ref.subscribe(changed)
    try:
        try:
            with root.pass_scope():
                with root.open_app_context_override(
                    outer_id, (key,), "discard"
                ) as outer:
                    with outer.open_app_context_override(
                        inner_id, (key,), None
                    ) as inner:
                        result["candidate"] = [
                            inner.get_authored_app_context(key),
                            inner.committed_values,
                        ]
                raise ValueError("discard")
        except ValueError:
            pass
        result["rollback"] = [ref.get(), list(observations)]
        with root.pass_scope():
            with root.open_app_context_override(outer_id, (key,), "new") as outer:
                with outer.open_app_context_override(inner_id, (key,), None) as inner:
                    result["stable_identity"] = (
                        inner.authored_app_context_ref(key).identity is ref.identity
                    )
        result["accepted"] = [ref.get(), list(observations)]
        with root.pass_scope():
            with root.open_app_context_override(outer_id, (key,), "new") as outer:
                with outer.open_app_context_override(inner_id, (key,), "concrete"):
                    pass
        result["concrete"] = [ref.get(), parent_ref.identity.has_subscribers()]
        with root.pass_scope():
            with root.open_app_context_override(outer_id, (key,), "other"):
                pass
        result["omitted"] = [
            parent_ref.identity.has_subscribers(),
            root.debug_is_active(inner_id),
            list(observations),
        ]
    finally:
        unsubscribe()
    return result


if __name__ == "__main__":
    print(json.dumps(characterize(), sort_keys=True))
