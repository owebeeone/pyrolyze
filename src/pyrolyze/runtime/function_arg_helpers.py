from __future__ import annotations

from typing import Any


def pack_function_args(
    param_names: tuple[str, ...],
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
) -> dict[str, Any]:
    if len(args) > len(param_names):
        raise TypeError("too many positional arguments for packed component call")
    packed = {param_names[index]: value for index, value in enumerate(args)}
    for key, value in kwargs.items():
        if key in packed:
            raise TypeError(f"multiple values for argument {key!r}")
        packed[key] = value
    return packed


def build_function_arg_dirty_map(
    param_names: tuple[str, ...],
    args_dirty: tuple[Any, ...],
    kwargs_dirty: dict[str, Any],
) -> dict[str, bool]:
    packed = pack_function_args(param_names, args_dirty, kwargs_dirty)
    return {key: bool(value) for key, value in packed.items()}
