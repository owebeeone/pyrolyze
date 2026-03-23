"""Live DearPyGui runtime host (context, viewport, staging root, item API)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class LiveDpgHost:
    """Imperative DearPyGui backend implementing :class:`DpgRuntimeHost`.

    Call :meth:`start` before mounting (or use as a context manager). Uses an
    ``add_stage`` staging root so ``detach_child`` and pre-attach items stay off
    the visible tree until reparented.
    """

    title: str = "PyRolyze"
    width: int = 800
    height: int = 600
    show_viewport: bool = True
    vsync: bool = False

    _dpg: Any | None = field(default=None, repr=False)
    _staging_tag: int | str = field(default=0, repr=False)
    _started: bool = field(default=False, repr=False)
    _tag_by_slot: dict[Any, int | str] = field(default_factory=dict, repr=False)
    parent_of: dict[int, int] = field(default_factory=dict, repr=False)
    children_order: dict[int, list[int]] = field(default_factory=dict, repr=False)

    @property
    def staging_tag(self) -> int | str:
        return self._staging_tag

    def _require_dpg(self) -> Any:
        if self._dpg is None:
            msg = "LiveDpgHost.start() must be called before using the host"
            raise RuntimeError(msg)
        return self._dpg

    def start(self) -> None:
        if self._started:
            return
        import dearpygui.dearpygui as dpg

        self._dpg = dpg
        dpg.create_context()
        dpg.create_viewport(title=self.title, width=self.width, height=self.height, vsync=self.vsync)
        dpg.setup_dearpygui()
        self._staging_tag = dpg.add_stage(label="__pyrolyze_staging__")
        self.children_order.setdefault(int(self._staging_tag), [])
        if self.show_viewport:
            dpg.show_viewport()
        self._started = True

    def stop(self) -> None:
        if not self._started or self._dpg is None:
            self._reset_state()
            return
        self._dpg.destroy_context()
        self._reset_state()

    def _reset_state(self) -> None:
        self._dpg = None
        self._staging_tag = 0
        self._started = False
        self._tag_by_slot.clear()
        self.parent_of.clear()
        self.children_order.clear()

    def __enter__(self) -> LiveDpgHost:
        self.start()
        return self

    def __exit__(self, *exc: object) -> None:
        self.stop()

    def allocate_tag(self, slot_id: Any | None = None) -> int | str:
        dpg = self._require_dpg()
        if slot_id is not None and slot_id in self._tag_by_slot:
            return self._tag_by_slot[slot_id]
        tag = dpg.generate_uuid()
        if slot_id is not None:
            self._tag_by_slot[slot_id] = tag
        self.children_order.setdefault(int(tag), [])
        return tag

    def create_with_factory(
        self,
        factory_name: str,
        slot_id: Any | None = None,
        **kwargs: Any,
    ) -> int | str:
        dpg = self._require_dpg()
        tag = self.allocate_tag(slot_id)
        factory = getattr(dpg, factory_name)
        merged = dict(kwargs)
        merged.pop("tag", None)
        merged.pop("parent", None)
        merged.pop("before", None)
        staging_i = int(self._staging_tag)
        relocate = False
        try:
            out = factory(tag=tag, parent=self._staging_tag, before=0, **merged)
        except (TypeError, SystemError):
            try:
                out = factory(tag=tag, parent=self._staging_tag, **merged)
            except (TypeError, SystemError):
                out = factory(tag=tag, **merged)
                relocate = True
        result_tag = int(out) if out is not None else int(tag)
        if relocate:
            self.move_item(result_tag, parent=staging_i, before=0)
        else:
            self._track_new_item(result_tag, staging_i)
        return result_tag

    def _track_new_item(self, item_i: int, parent_i: int) -> None:
        self.parent_of[item_i] = parent_i
        order = [c for c in self.children_order.setdefault(parent_i, []) if c != item_i]
        order.append(item_i)
        self.children_order[parent_i] = order

    def configure_item(self, item: int | str, **kwargs: Any) -> None:
        dpg = self._require_dpg()
        if not dpg.does_item_exist(item):
            return
        dpg.configure_item(item, **kwargs)

    def set_value(self, item: int | str, value: Any) -> None:
        dpg = self._require_dpg()
        item_i = int(item)
        if not dpg.does_item_exist(item_i):
            return
        dpg.set_value(item_i, value)

    def move_item(self, item: int | str, *, parent: int | str, before: int | str = 0) -> None:
        dpg = self._require_dpg()
        item_i = int(item)
        parent_i = int(parent)
        before_i = int(before) if before != 0 else 0
        if not dpg.does_item_exist(item_i):
            return
        dpg.move_item(item_i, parent=parent_i, before=before_i)
        old_parent = self.parent_of.get(item_i)
        if old_parent is not None:
            self.children_order[old_parent] = [c for c in self.children_order[old_parent] if c != item_i]
        self.parent_of[item_i] = parent_i
        order = [c for c in self.children_order.setdefault(parent_i, []) if c != item_i]
        if before_i == 0:
            order.append(item_i)
        else:
            idx = order.index(before_i) if before_i in order else len(order)
            order.insert(idx, item_i)
        self.children_order[parent_i] = order

    def delete_item(self, item: int | str) -> None:
        dpg = self._require_dpg()
        item_i = int(item)
        if not dpg.does_item_exist(item_i):
            return
        dpg.delete_item(item_i)
        for sid, t in list(self._tag_by_slot.items()):
            if int(t) == item_i:
                del self._tag_by_slot[sid]
        old = self.parent_of.pop(item_i, None)
        if old is not None:
            self.children_order[old] = [c for c in self.children_order[old] if c != item_i]

    def get_config_value(self, item: int | str, key: str) -> Any:
        dpg = self._require_dpg()
        item_i = int(item)
        if not dpg.does_item_exist(item_i):
            return None
        cfg = dpg.get_item_configuration(item_i)
        return cfg.get(key)

    def get_item_value(self, item: int | str) -> Any:
        dpg = self._require_dpg()
        item_i = int(item)
        if not dpg.does_item_exist(item_i):
            return None
        return dpg.get_value(item_i)


__all__ = ["LiveDpgHost"]
