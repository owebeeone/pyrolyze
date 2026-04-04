from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from .model import PyroHostSurface, PyroNode


def describe_pyro_node_diff(
    actual: PyroNode,
    expected: PyroNode,
    *,
    compare_host_handles: bool = False,
) -> str | None:
    return _diff_node(
        actual,
        expected,
        path="root",
        compare_host_handles=compare_host_handles,
    )


def _diff_node(
    actual: PyroNode,
    expected: PyroNode,
    *,
    path: str,
    compare_host_handles: bool,
) -> str | None:
    if actual.node_type != expected.node_type:
        return _with_context(
            f"{path}.node_type: actual={actual.node_type!r} expected={expected.node_type!r}",
            actual,
            expected,
        )
    if dict(actual.kwargs) != dict(expected.kwargs):
        return _diff_mapping(
            dict(actual.kwargs),
            dict(expected.kwargs),
            path=f"{path}.kwargs",
            actual_node=actual,
            expected_node=expected,
        )
    if tuple(actual.args) != tuple(expected.args):
        return _diff_sequence(
            tuple(actual.args),
            tuple(expected.args),
            path=f"{path}.args",
            actual_node=actual,
            expected_node=expected,
        )

    mount_names = tuple(sorted(set(actual.mounts) | set(expected.mounts)))
    for mount_name in mount_names:
        if mount_name not in actual.mounts:
            return _with_context(f"{path}.mounts[{mount_name!r}]: missing in actual", actual, expected)
        if mount_name not in expected.mounts:
            return _with_context(f"{path}.mounts[{mount_name!r}]: unexpected in actual", actual, expected)
        actual_buckets = actual.mounts[mount_name]
        expected_buckets = expected.mounts[mount_name]
        if len(actual_buckets) != len(expected_buckets):
            return _with_context(
                f"{path}.mounts[{mount_name!r}]: bucket count actual={len(actual_buckets)} "
                f"expected={len(expected_buckets)}",
                actual,
                expected,
            )
        for bucket_index, (actual_bucket, expected_bucket) in enumerate(
            zip(actual_buckets, expected_buckets, strict=False)
        ):
            bucket_path = f"{path}.mounts[{mount_name!r}][{bucket_index}]"
            if actual_bucket.key != expected_bucket.key:
                return _with_context(
                    f"{bucket_path}.key: actual={actual_bucket.key!r} expected={expected_bucket.key!r}",
                    actual,
                    expected,
                )
            if actual_bucket.values != expected_bucket.values:
                return _with_context(
                    f"{bucket_path}.values: actual={actual_bucket.values!r} "
                    f"expected={expected_bucket.values!r}",
                    actual,
                    expected,
                )
            if len(actual_bucket.entries) != len(expected_bucket.entries):
                return _with_context(
                    f"{bucket_path}.entries: count actual={len(actual_bucket.entries)} "
                    f"expected={len(expected_bucket.entries)}",
                    actual,
                    expected,
                )
            for entry_index, (actual_entry, expected_entry) in enumerate(
                zip(actual_bucket.entries, expected_bucket.entries, strict=False)
            ):
                entry_path = f"{bucket_path}.entries[{entry_index}]"
                if actual_entry.placement_id != expected_entry.placement_id:
                    return _with_context(
                        f"{entry_path}.placement_id: actual={actual_entry.placement_id!r} "
                        f"expected={expected_entry.placement_id!r}",
                        actual,
                        expected,
                    )
                nested = _diff_node(
                    actual_entry.node,
                    expected_entry.node,
                    path=f"{entry_path}.node",
                    compare_host_handles=compare_host_handles,
                )
                if nested is not None:
                    return nested

    surface_names = tuple(sorted(set(actual.host_surfaces) | set(expected.host_surfaces)))
    for surface_name in surface_names:
        if surface_name not in actual.host_surfaces:
            return _with_context(f"{path}.host_surfaces[{surface_name!r}]: missing in actual", actual, expected)
        if surface_name not in expected.host_surfaces:
            return _with_context(f"{path}.host_surfaces[{surface_name!r}]: unexpected in actual", actual, expected)
        nested = _diff_host_surface(
            actual.host_surfaces[surface_name],
            expected.host_surfaces[surface_name],
            path=f"{path}.host_surfaces[{surface_name!r}]",
            actual_node=actual,
            expected_node=expected,
            compare_host_handles=compare_host_handles,
        )
        if nested is not None:
            return nested

    return None


def _diff_host_surface(
    actual: PyroHostSurface,
    expected: PyroHostSurface,
    *,
    path: str,
    actual_node: PyroNode,
    expected_node: PyroNode,
    compare_host_handles: bool,
) -> str | None:
    if actual.surface_name != expected.surface_name:
        return _with_context(
            f"{path}.surface_name: actual={actual.surface_name!r} expected={expected.surface_name!r}",
            actual_node,
            expected_node,
        )
    if len(actual.entries) != len(expected.entries):
        return _with_context(
            f"{path}.entries: count actual={len(actual.entries)} expected={len(expected.entries)}",
            actual_node,
            expected_node,
        )
    for index, (actual_entry, expected_entry) in enumerate(zip(actual.entries, expected.entries, strict=False)):
        entry_path = f"{path}.entries[{index}]"
        if compare_host_handles and actual_entry.placement_handle != expected_entry.placement_handle:
            return _with_context(
                f"{entry_path}.placement_handle: actual={actual_entry.placement_handle!r} "
                f"expected={expected_entry.placement_handle!r}",
                actual_node,
                expected_node,
            )
        if actual_entry.child_kind != expected_entry.child_kind:
            return _with_context(
                f"{entry_path}.child_kind: actual={actual_entry.child_kind!r} "
                f"expected={expected_entry.child_kind!r}",
                actual_node,
                expected_node,
            )
        nested = _diff_node(
            actual_entry.node,
            expected_entry.node,
            path=f"{entry_path}.node",
            compare_host_handles=compare_host_handles,
        )
        if nested is not None:
            return nested
    return None


def _diff_mapping(
    actual: Mapping[str, Any],
    expected: Mapping[str, Any],
    *,
    path: str,
    actual_node: PyroNode,
    expected_node: PyroNode,
) -> str | None:
    keys = tuple(sorted(set(actual) | set(expected)))
    for key in keys:
        if key not in actual:
            return _with_context(
                f"{path}[{key!r}]: missing in actual",
                actual_node,
                expected_node,
            )
        if key not in expected:
            return _with_context(
                f"{path}[{key!r}]: unexpected in actual",
                actual_node,
                expected_node,
            )
        actual_value = actual[key]
        expected_value = expected[key]
        if actual_value != expected_value:
            return _with_context(
                f"{path}[{key!r}]: actual={actual_value!r} expected={expected_value!r}",
                actual_node,
                expected_node,
            )
    return None


def _diff_sequence(
    actual: Sequence[Any],
    expected: Sequence[Any],
    *,
    path: str,
    actual_node: PyroNode,
    expected_node: PyroNode,
) -> str | None:
    if len(actual) != len(expected):
        return _with_context(
            f"{path}: length actual={len(actual)} expected={len(expected)}",
            actual_node,
            expected_node,
        )
    for index, (actual_value, expected_value) in enumerate(zip(actual, expected, strict=False)):
        if actual_value != expected_value:
            return _with_context(
                f"{path}[{index}]: actual={actual_value!r} expected={expected_value!r}",
                actual_node,
                expected_node,
            )
    return None


def _with_context(message: str, actual: PyroNode, expected: PyroNode) -> str:
    return "\n".join(
        (
            message,
            f"actual node:   {_node_summary(actual)}",
            f"expected node: {_node_summary(expected)}",
            f"actual children:   {_child_summaries(actual)}",
            f"expected children: {_child_summaries(expected)}",
        )
    )


def _node_summary(node: PyroNode) -> str:
    name = node.kwargs.get("name")
    label = node.kwargs.get("label")
    parts = [node.node_type]
    if name is not None:
        parts.append(f"name={name!r}")
    if label is not None:
        parts.append(f"label={label!r}")
    return ", ".join(parts)


def _child_summaries(node: PyroNode) -> str:
    parts: list[str] = []
    for mount_name, buckets in node.mounts.items():
        for bucket_index, bucket in enumerate(buckets):
            entries = ", ".join(_node_summary(entry.node) for entry in bucket.entries)
            parts.append(f"{mount_name}[{bucket_index}]=[{entries}]")
    return "; ".join(parts) if parts else "<none>"


__all__ = ["describe_pyro_node_diff"]
