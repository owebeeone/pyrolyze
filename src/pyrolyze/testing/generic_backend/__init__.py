"""Generic generated backend support for PyRolyze tests."""

from .api import BuildPyroNodeBackend
from .diff import describe_pyro_node_diff
from .engine import PyroNodeEngine
from .fuzz import (
    FuzzReplayRecord,
    FuzzReplayStep,
    HostSurfaceReplayState,
    capture_host_surface_replay_state,
    generate_argument_fuzz_replay,
)
from .harness import PyroRenderHarness, PyroRenderResult
from .model import (
    PyroArgs,
    PyroHostSurface,
    PyroHostSurfaceEntry,
    PyroHostSurfaceOperation,
    PyroMountBucket,
    PyroMountEntry,
    PyroMountOperation,
    PyroNode,
)
from .runtime import PyrolyzeMountCompatibilityError
from .snapshots import PyroUiElement, PyroUiMountAdvertisement, PyroUiMountDirective, run_pyro, run_pyro_ui
from .specs import (
    HostPlacementChildKind,
    HostPlacementProfile,
    HostSurfaceReconcileMode,
    HostSurfaceStyle,
    MountInterfaceKind,
    MountParam,
    MountPointProfile,
    MountSpec,
    MountStyleVariant,
    MountVariantSpec,
    NodeGenSpec,
    ParamSpec,
    validate_node_specs,
)

__all__ = [
    "BuildPyroNodeBackend",
    "describe_pyro_node_diff",
    "FuzzReplayRecord",
    "FuzzReplayStep",
    "HostSurfaceReplayState",
    "HostPlacementChildKind",
    "HostPlacementProfile",
    "HostSurfaceReconcileMode",
    "HostSurfaceStyle",
    "PyroHostSurface",
    "PyroHostSurfaceEntry",
    "PyroHostSurfaceOperation",
    "MountInterfaceKind",
    "MountParam",
    "MountPointProfile",
    "MountSpec",
    "MountStyleVariant",
    "MountVariantSpec",
    "NodeGenSpec",
    "ParamSpec",
    "PyroArgs",
    "PyroRenderHarness",
    "PyroRenderResult",
    "PyroMountBucket",
    "PyroMountEntry",
    "PyroMountOperation",
    "PyroNode",
    "PyroNodeEngine",
    "PyroUiElement",
    "PyroUiMountAdvertisement",
    "PyroUiMountDirective",
    "PyrolyzeMountCompatibilityError",
    "capture_host_surface_replay_state",
    "run_pyro",
    "run_pyro_ui",
    "generate_argument_fuzz_replay",
    "validate_node_specs",
]
