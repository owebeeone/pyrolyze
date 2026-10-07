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


@pytest.mark.parametrize("implementation", ("original", "lcm"))
def test_reference_callback_selection_baseline(implementation: str) -> None:
    environment = dict(os.environ)
    environment.pop("PYROLYZE_USE_CONTEXT_LCM", None)
    environment["PYROLYZE_CONTEXT_IMPL"] = implementation
    _check_baseline("callback_selection.py", "callback_selection", environment)


def _check_baseline(script: str, name: str, environment: dict[str, str]) -> None:
    expected = json.loads(
        (_DATA / "baselines" / f"{name}.json").read_text(encoding="utf-8")
    )
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    result = subprocess.run(
        [sys.executable, str(_DATA / script)],
        cwd=_ROOT,
        env=environment,
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout) == expected
