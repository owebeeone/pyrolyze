from __future__ import annotations

from pyrolyze.runtime.dirt import DM


def test_dm_literal_dirty_only_on_initial_render() -> None:
    dm = DM()

    assert dm.bind.unknown_name is True


def test_dm_bind_lookup_and_default_local_dirt() -> None:
    dm = DM()

    assert dm.bind.unknown_name is True

    dm.bind.value = False
    assert dm.bind.value is False


def test_dm_bind_assignment_unpacks_tuple_shape() -> None:
    dm = DM()

    dm.bind.val, dm.bind.func = (True, False)

    assert dm.bind.val is True
    assert dm.bind.func is False


def test_dm_bind_proxy_keeps_tuple_assignment_pythonic() -> None:
    dm = DM()

    dm.bind.result = (True, False)

    assert dm.bind.result == (True, False)


def test_dm_structural_is_dirty() -> None:
    dm = DM()

    assert dm.is_dirty(False) is False
    assert dm.is_dirty(True) is True
    assert dm.is_dirty((False, False)) is False
    assert dm.is_dirty((True, False)) is True
    assert dm.is_dirty([False, True]) is True
    assert dm.is_dirty({"a": False, "b": True}) is True


def test_dm_clean_shape_like() -> None:
    dm = DM()

    assert dm.clean_shape_like(("x", "y")) == (False, False)
    assert dm.clean_shape_like(["x", "y"]) == [False, False]
    assert dm.clean_shape_like({"a": 1, "b": 2}) == {"a": False, "b": False}


def test_dm_delete_removes_binding() -> None:
    dm = DM()
    dm.bind.value = False

    del dm.bind.value

    assert dm.bind.value is True
