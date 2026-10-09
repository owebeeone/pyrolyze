from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

_ROOT = Path(__file__).resolve().parents[1]
_DATA = _ROOT / "tests" / "data" / "lcm_integration"


@pytest.mark.parametrize("implementation", ("original", "lcm", "bare_refactor_lcm"))
def test_lcm_integration_characterization_baseline(implementation: str) -> None:
    environment = dict(os.environ)
    environment.pop("PYROLYZE_USE_CONTEXT_LCM", None)
    environment["PYROLYZE_CONTEXT_IMPL"] = implementation
    _check_baseline("characterize.py", implementation, environment)


def test_lifecycle_completion_outcomes_l0_target() -> None:
    _check_baseline(
        "transaction_completion_outcomes.py",
        "transaction_completion_outcomes",
        dict(os.environ),
    )


def test_lifecycle_shared_completion_characterization_baseline() -> None:
    _check_baseline("shared_completion.py", "shared_completion", dict(os.environ))


def test_common_slot_construction_golden() -> None:
    _check_baseline("slot_construction.py", "slot_construction", dict(os.environ))


def test_common_pass_single_cohort_golden() -> None:
    _check_baseline(
        "common_pass_single_cohort.py", "common_pass_single_cohort", dict(os.environ)
    )


def test_callback_selection_lifecycle_golden() -> None:
    _check_baseline(
        "callback_selection_lifecycle.py",
        "callback_selection_lifecycle",
        dict(os.environ),
    )


def test_invocation_values_lifecycle_golden() -> None:
    _check_baseline(
        "invocation_values_lifecycle.py",
        "invocation_values_lifecycle",
        dict(os.environ),
    )


def test_slot_call_values_lifecycle_golden() -> None:
    _check_baseline(
        "slot_call_values_lifecycle.py",
        "slot_call_values_lifecycle",
        dict(os.environ),
    )


def test_subscription_selection_lifecycle_golden() -> None:
    _check_baseline(
        "subscription_selection_lifecycle.py",
        "subscription_selection_lifecycle",
        dict(os.environ),
    )


def test_effect_selection_lifecycle_golden() -> None:
    _check_baseline(
        "effect_selection_lifecycle.py", "effect_selection_lifecycle", dict(os.environ)
    )


def test_async_effect_selection_lifecycle_golden() -> None:
    _check_baseline(
        "async_effect_selection_lifecycle.py",
        "async_effect_selection_lifecycle",
        dict(os.environ),
    )


def test_mount_selection_lifecycle_golden() -> None:
    _check_baseline(
        "mount_selection_lifecycle.py", "mount_selection_lifecycle", dict(os.environ)
    )


def test_keyed_loop_lifecycle_golden() -> None:
    _check_baseline("keyed_loop_lifecycle.py", "keyed_loop_lifecycle", dict(os.environ))


def test_container_routing_lifecycle_golden() -> None:
    _check_baseline("container_routing_lifecycle.py", "container_routing_lifecycle", dict(os.environ))


def test_pass_state_lifecycle_golden() -> None:
    _check_baseline("pass_state_lifecycle.py", "pass_state_lifecycle", dict(os.environ))


@pytest.mark.parametrize(
    "name",
    (
        "slot_call_values_lifecycle",
        "subscription_selection_lifecycle",
        "effect_selection_lifecycle",
        "async_effect_selection_lifecycle",
        "mount_selection_lifecycle",
        "keyed_loop_lifecycle",
        "container_routing_lifecycle",
    ),
)
def test_resource_checkpoint_with_lifecycle_pass_state(name: str) -> None:
    _check_baseline(f"{name}.py", name, dict(os.environ), pass_state=True)


def test_directive_completion_lifecycle_golden() -> None:
    _check_baseline(
        "directive_completion_lifecycle.py", "directive_completion_lifecycle", dict(os.environ)
    )


def test_override_selection_lifecycle_golden() -> None:
    _check_baseline(
        "override_selection_lifecycle.py", "override_selection_lifecycle", dict(os.environ)
    )


def test_component_selection_lifecycle_golden() -> None:
    _check_baseline(
        "component_selection_lifecycle.py", "component_selection_lifecycle", dict(os.environ)
    )


def test_expression_mount_lifecycle_golden() -> None:
    _check_baseline(
        "expression_mount_lifecycle.py", "expression_mount_lifecycle", dict(os.environ)
    )


def test_expression_async_effect_lifecycle_golden() -> None:
    _check_baseline(
        "expression_async_effect_lifecycle.py",
        "expression_async_effect_lifecycle",
        dict(os.environ),
    )


def test_expression_effect_lifecycle_golden() -> None:
    _check_baseline(
        "expression_effect_lifecycle.py",
        "expression_effect_lifecycle",
        dict(os.environ),
    )


def test_expression_subscription_lifecycle_golden() -> None:
    _check_baseline(
        "expression_subscription_lifecycle.py",
        "expression_subscription_lifecycle",
        dict(os.environ),
    )


def test_slot_expr_selection_lifecycle_golden() -> None:
    _check_baseline(
        "slot_expr_selection_lifecycle.py", "slot_expr_selection_lifecycle", dict(os.environ)
    )


@pytest.mark.parametrize("implementation", ("original", "bare_refactor_lcm"))
def test_common_pass_preflight_baseline(implementation: str) -> None:
    environment = dict(os.environ)
    environment.pop("PYROLYZE_USE_CONTEXT_LCM", None)
    environment["PYROLYZE_CONTEXT_IMPL"] = implementation
    _check_baseline(
        "common_pass_preflight.py",
        f"common_pass_preflight_{implementation}",
        environment,
    )


@pytest.mark.parametrize("implementation", ("original", "lcm", "bare_refactor_lcm"))
def test_reference_callback_selection_baseline(implementation: str) -> None:
    environment = dict(os.environ)
    environment.pop("PYROLYZE_USE_CONTEXT_LCM", None)
    environment["PYROLYZE_CONTEXT_IMPL"] = implementation
    _check_baseline("callback_selection.py", "callback_selection", environment)


@pytest.mark.parametrize("implementation", ("original", "lcm", "bare_refactor_lcm"))
def test_reference_owned_callback_selection_baseline(implementation: str) -> None:
    environment = dict(os.environ)
    environment.pop("PYROLYZE_USE_CONTEXT_LCM", None)
    environment["PYROLYZE_CONTEXT_IMPL"] = implementation
    _check_baseline(
        "callback_owned_selection.py", "callback_owned_selection", environment
    )


def _check_baseline(
    script: str,
    name: str,
    environment: dict[str, str],
    *,
    pass_state: bool = False,
) -> None:
    expected = json.loads(
        (_DATA / "baselines" / f"{name}.json").read_text(encoding="utf-8")
    )
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    command = [sys.executable, str(_DATA / script)]
    if pass_state:
        # Replay the existing canonical resource contract with the newest gate,
        # rather than copy success assertions into a second set of unit tests.
        command = [sys.executable, "-c", """
import json
import runpy
import sys
from pathlib import Path
from pyrolyze.runtime.context_state_lcm.pass_state_render import _enable_pass_state_render

script = Path(sys.argv[1])
sys.path.insert(0, str(script.parent))
namespace = runpy.run_path(str(script))
entry = namespace.get('characterize') or namespace['observe']
scope = entry.__globals__
for name in tuple(scope):
    if name.startswith('_enable_') and name.endswith('_render'):
        scope[name] = _enable_pass_state_render
print(json.dumps(entry(), sort_keys=True))
""", str(_DATA / script)]
    result = subprocess.run(
        command,
        cwd=_ROOT,
        env=environment,
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout) == expected
