from __future__ import annotations

from dataclasses import FrozenInstanceError
import pytest

from pyrolyze.freezable import HintResolutionMode, freezable_dataclass, frozen_dataclass


def test_freezable_and_frozen_dataclass_round_trip_with_frozen_post_init() -> None:
    events: list[tuple[int, int]] = []

    @freezable_dataclass(frozen_type="FrozenMyClass")
    class MyClass:
        x: int
        y: int

    @frozen_dataclass(mutable_type=MyClass)
    class FrozenMyClass:
        def __post_init__(self) -> None:
            events.append((self.x, self.y))

    value = MyClass(1, 2)
    value.x = 10

    frozen = value.to_frozen()

    assert isinstance(frozen, FrozenMyClass)
    assert events == [(10, 2)]
    assert FrozenMyClass(x=1, y=2) == MyClass(x=1, y=2).to_frozen()
    assert hash(FrozenMyClass(x=1, y=2)) == hash(MyClass(x=1, y=2).to_frozen())

    with pytest.raises(FrozenInstanceError):
        frozen.x = 20

    mutable = frozen.to_mutable()
    assert isinstance(mutable, MyClass)
    mutable.x = 30
    assert mutable.x == 30


def test_frozen_dataclass_can_generate_default_frozen_peer() -> None:
    @freezable_dataclass(frozen_type="FrozenMyClass")
    class MyClass:
        x: int
        y: int

    @frozen_dataclass(mutable_type=MyClass)
    class FrozenMyClass:
        pass

    frozen = MyClass(3, 4).to_frozen()

    assert type(frozen).__name__ == "FrozenMyClass"
    assert isinstance(hash(frozen), int)

    with pytest.raises(FrozenInstanceError):
        frozen.y = 5

    mutable = frozen.to_mutable()
    assert isinstance(mutable, MyClass)
    assert mutable.x == 3
    assert mutable.y == 4


def test_frozen_and_mutable_kin_do_not_currently_compare_equal() -> None:
    @freezable_dataclass(frozen_type="FrozenMyClass")
    class MyClass:
        x: int
        y: int

    @frozen_dataclass(mutable_type=MyClass)
    class FrozenMyClass:
        pass

    assert FrozenMyClass(x=1, y=2) != MyClass(x=1, y=2)


def test_frozen_dataclass_inherits_from_frozen_base_peer() -> None:
    @freezable_dataclass(frozen_type="FrozenBase")
    class Base:
        a: int

    @freezable_dataclass(frozen_type="FrozenChild")
    class Child(Base):
        b: int

    @frozen_dataclass(mutable_type=Base)
    class FrozenBase:
        pass

    @frozen_dataclass(mutable_type=Child)
    class FrozenChild:
        pass

    frozen = Child(a=1, b=2).to_frozen()

    assert isinstance(frozen, FrozenChild)
    assert isinstance(frozen, FrozenBase)
    assert frozen.a == 1
    assert frozen.b == 2
    assert frozen.to_mutable() == Child(a=1, b=2)


def test_frozen_dataclass_raises_when_frozen_base_peer_is_missing() -> None:
    @freezable_dataclass(frozen_type="FrozenBase")
    class Base:
        a: int

    @freezable_dataclass(frozen_type="FrozenChild")
    class Child(Base):
        b: int

    with pytest.raises(AttributeError, match="FrozenBase"):
        @frozen_dataclass(mutable_type=Child)
        class FrozenChild:
            pass


def test_freezable_nested_fields_are_converted() -> None:
    @freezable_dataclass(frozen_type="FrozenChild")
    class Child:
        value: int

    @frozen_dataclass(mutable_type=Child)
    class FrozenChild:
        pass

    @freezable_dataclass(frozen_type="FrozenParent")
    class Parent:
        child: Child

    @frozen_dataclass(mutable_type=Parent)
    class FrozenParent:
        pass

    parent = Parent(child=Child(value=7))
    frozen = parent.to_frozen()

    assert isinstance(frozen, FrozenParent)
    assert isinstance(frozen.child, FrozenChild)
    assert frozen.child.value == 7

    mutable = frozen.to_mutable()
    assert isinstance(mutable.child, Child)
    assert mutable == parent


def test_freezable_list_fields_round_trip_as_tuple_and_back() -> None:
    @freezable_dataclass(frozen_type="FrozenItem")
    class Item:
        value: int

    @frozen_dataclass(mutable_type=Item)
    class FrozenItem:
        pass

    @freezable_dataclass(frozen_type="FrozenBag")
    class Bag:
        items: list[Item]
        labels: list[str]

    @frozen_dataclass(mutable_type=Bag)
    class FrozenBag:
        pass

    bag = Bag(items=[Item(1), Item(2)], labels=["a", "b"])
    frozen = bag.to_frozen()

    assert isinstance(frozen.items, tuple)
    assert isinstance(frozen.labels, tuple)
    assert all(isinstance(item, FrozenItem) for item in frozen.items)
    assert tuple(item.value for item in frozen.items) == (1, 2)
    assert frozen.labels == ("a", "b")

    mutable = frozen.to_mutable()
    assert isinstance(mutable.items, list)
    assert isinstance(mutable.labels, list)
    assert all(isinstance(item, Item) for item in mutable.items)
    assert [item.value for item in mutable.items] == [1, 2]
    assert mutable.labels == ["a", "b"]


def test_hint_resolution_mode_strict_module_does_not_resolve_local_forward_refs() -> None:
    @freezable_dataclass(
        frozen_type="FrozenItem",
        hint_resolution=HintResolutionMode.STRICT_MODULE,
    )
    class Item:
        value: int

    @frozen_dataclass(
        mutable_type=Item,
        hint_resolution=HintResolutionMode.STRICT_MODULE,
    )
    class FrozenItem:
        pass

    @freezable_dataclass(
        frozen_type="FrozenBag",
        hint_resolution=HintResolutionMode.STRICT_MODULE,
    )
    class Bag:
        items: list[Item]

    @frozen_dataclass(
        mutable_type=Bag,
        hint_resolution=HintResolutionMode.STRICT_MODULE,
    )
    class FrozenBag:
        pass

    frozen = Bag(items=[Item(1)]).to_frozen()
    assert isinstance(frozen.items, list)
    assert isinstance(frozen.items[0], Item)


def test_hint_resolution_mode_frame_with_fallback_resolves_local_forward_refs() -> None:
    @freezable_dataclass(
        frozen_type="FrozenItem",
        hint_resolution=HintResolutionMode.FRAME_WITH_FALLBACK,
    )
    class Item:
        value: int

    @frozen_dataclass(
        mutable_type=Item,
        hint_resolution=HintResolutionMode.FRAME_WITH_FALLBACK,
    )
    class FrozenItem:
        pass

    @freezable_dataclass(
        frozen_type="FrozenBag",
        hint_resolution=HintResolutionMode.FRAME_WITH_FALLBACK,
    )
    class Bag:
        items: list[Item]

    @frozen_dataclass(
        mutable_type=Bag,
        hint_resolution=HintResolutionMode.FRAME_WITH_FALLBACK,
    )
    class FrozenBag:
        pass

    frozen = Bag(items=[Item(1)]).to_frozen()
    assert isinstance(frozen.items, tuple)
    assert isinstance(frozen.items[0], FrozenItem)
