from __future__ import annotations

import argparse
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
from typing import TextIO
import tomllib
from typing import Sequence


_KERNEL_TAG_RE = re.compile(r"^v(?P<major>\d+)_(?P<minor>\d+)$")


def discover_supported_kernel_tags(project_root: Path) -> tuple[str, ...]:
    kernels_dir = project_root / "src" / "pyrolyze" / "compiler" / "kernels"
    tags: list[str] = []
    if not kernels_dir.exists():
        return ()
    for entry in kernels_dir.iterdir():
        if entry.is_dir() and _KERNEL_TAG_RE.match(entry.name):
            tags.append(entry.name)
    return tuple(sorted(tags, key=_parse_kernel_tag))


def normalize_kernel_tag(value: str) -> str:
    raw = value.strip()
    match = _KERNEL_TAG_RE.match(raw)
    if match is not None:
        return raw

    if "." in raw:
        major, minor = raw.split(".", 1)
    elif "_" in raw:
        major, minor = raw.split("_", 1)
    else:
        raise ValueError(f"Unsupported kernel version spelling: {value!r}")
    return f"v{int(major)}_{int(minor)}"


def kernel_tag_for_runtime(
    runtime_version: tuple[int, int],
    supported_kernel_tags: Sequence[str],
) -> str:
    if not supported_kernel_tags:
        raise ValueError("No supported kernel tags were discovered.")
    requested = normalize_kernel_tag(f"{runtime_version[0]}.{runtime_version[1]}")
    if requested in supported_kernel_tags:
        return requested
    return max(supported_kernel_tags, key=_parse_kernel_tag)


def runtime_tag(runtime_version: tuple[int, int]) -> str:
    return f"py{runtime_version[0]}_{runtime_version[1]}"


def actual_results_dir(
    project_root: Path,
    *,
    runtime_version: tuple[int, int],
    kernel_tag: str,
) -> Path:
    return project_root / "tests" / "actual_test_results" / runtime_tag(runtime_version) / normalize_kernel_tag(kernel_tag)


def data_gold_src_dir(project_root: Path) -> Path:
    return project_root / "tests" / "data" / "gold_src"


def data_golden_dir(project_root: Path, *, kernel_tag: str) -> Path:
    return project_root / "tests" / "data" / normalize_kernel_tag(kernel_tag) / "goldens"


def golden_case_manifest_path(project_root: Path) -> Path:
    return project_root / "tests" / "data" / "gold_cases.toml"


def load_golden_cases(project_root: Path) -> dict[str, str]:
    manifest_path = golden_case_manifest_path(project_root)
    payload = tomllib.loads(manifest_path.read_text(encoding="utf-8"))
    cases = payload.get("cases", {})
    return {str(name): str(module_name) for name, module_name in cases.items()}


def load_supported_runtime_specs(pyproject_path: Path) -> tuple[str, ...]:
    payload = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))
    runtimes = payload.get("tool", {}).get("pyrolyze", {}).get("test-matrix", {}).get("python", [])
    return tuple(str(runtime) for runtime in runtimes)


def resolve_requested_runtime_specs(
    pyproject_path: Path,
    *,
    requested: Sequence[str] | None,
) -> tuple[str, ...]:
    raw_specs = load_supported_runtime_specs(pyproject_path) if requested is None else tuple(requested)
    normalized: list[str] = []
    for spec in raw_specs:
        major, minor = _version_tuple_from_python_spec(spec)
        normalized_spec = f"{major}.{minor}"
        if normalized_spec not in normalized:
            normalized.append(normalized_spec)
    return tuple(normalized)


def load_install_requirements(pyproject_path: Path) -> list[str]:
    payload = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))
    build_requires = list(payload.get("build-system", {}).get("requires", []))
    project = payload.get("project", {})
    dependencies = list(project.get("dependencies", []))
    optional_test = list(project.get("optional-dependencies", {}).get("test", []))

    requirements: list[str] = []
    for requirement in [*build_requires, *dependencies, *optional_test]:
        if requirement not in requirements:
            requirements.append(requirement)
    return requirements


def write_golden_outputs(
    project_root: Path,
    *,
    kernel_tag: str,
    output_dir: Path,
) -> None:
    from pyrolyze.compiler import emit_transformed_source

    source_dir = data_gold_src_dir(project_root)
    if not source_dir.exists():
        raise FileNotFoundError(f"Golden source directory does not exist: {source_dir}")

    output_dir.mkdir(parents=True, exist_ok=True)
    for file_name, module_name in load_golden_cases(project_root).items():
        source_path = source_dir / file_name
        transformed = emit_transformed_source(
            source_path.read_text(encoding="utf-8"),
            module_name=module_name,
            filename=str(source_path),
        )
        (output_dir / file_name).write_text(transformed + "\n", encoding="utf-8")


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Manage versioned PyRolyze golden and test runs.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_versions = subparsers.add_parser("list-versions", help="List supported AST kernel versions.")
    list_versions.set_defaults(func=_cmd_list_versions)

    regen = subparsers.add_parser(
        "regen-goldens",
        help="Regenerate checked-in goldens for one or more supported kernel versions via matching uv venvs.",
    )
    regen.add_argument("--versions", nargs="*", default=None, help="Kernel versions like v3_14 or 3.14. Defaults to all.")
    regen.add_argument(
        "--venv-root",
        default="tests/.uv-venvs",
        help="Directory for uv-managed versioned virtual environments.",
    )
    regen.add_argument(
        "--skip-missing-python",
        action="store_true",
        help="Skip versions whose exact interpreter cannot be provisioned.",
    )
    regen.set_defaults(func=_cmd_regen_goldens)

    run_tests = subparsers.add_parser(
        "run-tests",
        help="Create or reuse a uv venv for a selected Python version and run pytest inside it.",
    )
    run_tests.add_argument(
        "--python",
        required=True,
        help="Python version or executable accepted by uv, for example 3.14 or /path/to/python3.14.",
    )
    run_tests.add_argument(
        "--venv-root",
        default="tests/.uv-venvs",
        help="Directory for uv-managed versioned virtual environments.",
    )
    run_tests.add_argument(
        "--recreate",
        action="store_true",
        help="Delete and recreate the target uv environment before installing.",
    )
    run_tests.add_argument(
        "--pytest-args",
        nargs=argparse.REMAINDER,
        default=[],
        help="Arguments forwarded to pytest after '--pytest-args'.",
    )
    run_tests.set_defaults(func=_cmd_run_tests)

    run_tests_all = subparsers.add_parser(
        "run-tests-all",
        help="Run the test suite for multiple selected Python versions in parallel.",
    )
    run_tests_all.add_argument(
        "--python",
        nargs="*",
        default=None,
        help="Python versions to run, for example 3.12 3.13 3.14. Defaults to the supported matrix in pyproject.toml.",
    )
    run_tests_all.add_argument(
        "--venv-root",
        default="tests/.uv-venvs",
        help="Directory for uv-managed versioned virtual environments.",
    )
    run_tests_all.add_argument(
        "--recreate",
        action="store_true",
        help="Delete and recreate each target uv environment before installing.",
    )
    run_tests_all.add_argument(
        "--show-output",
        action="store_true",
        help="Print per-version run output even for passing runs. With one version selected, stream directly to stdout/stderr.",
    )
    run_tests_all.add_argument(
        "--pytest-args",
        nargs=argparse.REMAINDER,
        default=[],
        help="Arguments forwarded to pytest after '--pytest-args'.",
    )
    run_tests_all.set_defaults(func=_cmd_run_tests_all)

    internal = subparsers.add_parser(
        "_internal_regen_goldens",
        help=argparse.SUPPRESS,
    )
    internal.add_argument("--kernel-tag", required=True)
    internal.set_defaults(func=_cmd_internal_regen_goldens)

    return parser


def _cmd_list_versions(args: argparse.Namespace) -> int:
    project_root = Path(__file__).resolve().parents[1]
    for tag in discover_supported_kernel_tags(project_root):
        print(tag)
    return 0


def _cmd_regen_goldens(args: argparse.Namespace) -> int:
    project_root = Path(__file__).resolve().parents[1]
    supported = discover_supported_kernel_tags(project_root)
    requested = supported if args.versions is None else tuple(normalize_kernel_tag(value) for value in args.versions)
    venv_root = project_root / args.venv_root

    for kernel_tag in requested:
        if kernel_tag not in supported:
            raise SystemExit(f"Unsupported kernel tag: {kernel_tag}")

        python_spec = _python_spec_for_kernel(kernel_tag)
        try:
            venv_python = _ensure_uv_environment(
                project_root,
                python_spec=python_spec,
                venv_root=venv_root,
                recreate=False,
            )
        except subprocess.CalledProcessError:
            if args.skip_missing_python:
                print(f"Skipping {kernel_tag}: unable to provision Python {python_spec}", file=sys.stderr)
                continue
            raise

        _run(
            [
                str(venv_python),
                str(Path(__file__).resolve()),
                "_internal_regen_goldens",
                "--kernel-tag",
                kernel_tag,
            ],
            cwd=project_root,
        )
    return 0


def _cmd_run_tests(args: argparse.Namespace) -> int:
    project_root = Path(__file__).resolve().parents[1]
    venv_root = project_root / args.venv_root
    venv_python = _ensure_uv_environment(
        project_root,
        python_spec=args.python,
        venv_root=venv_root,
        recreate=args.recreate,
    )
    runtime_version = _query_python_version(venv_python)
    supported = discover_supported_kernel_tags(project_root)
    selected_kernel = kernel_tag_for_runtime(runtime_version, supported)
    results_dir = actual_results_dir(project_root, runtime_version=runtime_version, kernel_tag=selected_kernel)
    results_dir.mkdir(parents=True, exist_ok=True)

    pytest_args = list(args.pytest_args)
    if pytest_args and pytest_args[0] == "--":
        pytest_args = pytest_args[1:]

    junit_path = results_dir / "pytest.xml"
    env = os.environ.copy()
    env.setdefault("PYTHONUNBUFFERED", "1")

    command = [
        str(venv_python),
        "-m",
        "pytest",
        "--junitxml",
        str(junit_path),
        *pytest_args,
    ]
    if not pytest_args:
        command.append("-q")

    completed = _run(command, cwd=project_root, env=env, capture_output=True, check=False)
    (results_dir / "pytest.stdout.txt").write_text(completed.stdout or "", encoding="utf-8")
    (results_dir / "pytest.stderr.txt").write_text(completed.stderr or "", encoding="utf-8")
    sys.stdout.write(completed.stdout or "")
    sys.stderr.write(completed.stderr or "")
    return completed.returncode


def _cmd_run_tests_all(args: argparse.Namespace) -> int:
    project_root = Path(__file__).resolve().parents[1]
    runtime_specs = resolve_requested_runtime_specs(
        project_root / "pyproject.toml",
        requested=args.python,
    )
    if not runtime_specs:
        raise SystemExit("No runtime versions were selected for run-tests-all.")

    pytest_args = list(args.pytest_args)
    if pytest_args and pytest_args[0] == "--":
        pytest_args = pytest_args[1:]

    script_path = Path(__file__).resolve()
    env = os.environ.copy()
    env.setdefault("PYTHONUNBUFFERED", "1")

    if should_passthrough_run_tests_all_output(show_output=args.show_output, runtime_specs=runtime_specs):
        python_spec = runtime_specs[0]
        command = build_run_tests_invocation(
            script_path=script_path,
            python_executable=sys.executable,
            python_spec=python_spec,
            venv_root=args.venv_root,
            recreate=args.recreate,
            pytest_args=pytest_args,
        )
        completed = subprocess.run(
            command,
            cwd=str(project_root),
            env=env,
            check=False,
            text=True,
        )
        status = "PASS" if completed.returncode == 0 else f"FAIL ({completed.returncode})"
        print(f"{python_spec}: {status}")
        return completed.returncode

    processes: list[tuple[str, subprocess.Popen[str]]] = []

    for python_spec in runtime_specs:
        command = build_run_tests_invocation(
            script_path=script_path,
            python_executable=sys.executable,
            python_spec=python_spec,
            venv_root=args.venv_root,
            recreate=args.recreate,
            pytest_args=pytest_args,
        )
        process = subprocess.Popen(
            command,
            cwd=str(project_root),
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        processes.append((python_spec, process))

    overall = 0
    results: list[tuple[str, int, str, str]] = []
    for python_spec, process in processes:
        stdout, stderr = process.communicate()
        returncode = process.returncode or 0
        if returncode != 0:
            overall = 1
        results.append((python_spec, returncode, stdout or "", stderr or ""))

    report_run_tests_all_results(results, show_output=args.show_output)
    return overall


def _cmd_internal_regen_goldens(args: argparse.Namespace) -> int:
    project_root = Path(__file__).resolve().parents[1]
    kernel_tag = normalize_kernel_tag(args.kernel_tag)
    runtime_version = (sys.version_info.major, sys.version_info.minor)
    expected_runtime = _parse_kernel_tag(kernel_tag)
    if runtime_version != expected_runtime:
        raise SystemExit(
            f"Refusing to regenerate {kernel_tag} goldens under Python {runtime_version[0]}.{runtime_version[1]}; "
            f"use Python {expected_runtime[0]}.{expected_runtime[1]}."
        )

    output_dir = data_golden_dir(project_root, kernel_tag=kernel_tag)
    write_golden_outputs(project_root, kernel_tag=kernel_tag, output_dir=output_dir)
    return 0


def _ensure_uv_environment(
    project_root: Path,
    *,
    python_spec: str,
    venv_root: Path,
    recreate: bool,
) -> Path:
    venv_dir = venv_root / runtime_tag(_version_tuple_from_python_spec(python_spec))
    if recreate and venv_dir.exists():
        shutil.rmtree(venv_dir)

    venv_dir.parent.mkdir(parents=True, exist_ok=True)
    if not venv_dir.exists():
        _run(["uv", "venv", "--python", python_spec, str(venv_dir)], cwd=project_root)
    venv_python = _venv_python(venv_dir)

    requirements = load_install_requirements(project_root / "pyproject.toml")
    if requirements:
        _run(
            ["uv", "pip", "install", "--python", str(venv_python), *requirements],
            cwd=project_root,
        )
    _run(
        ["uv", "pip", "install", "--python", str(venv_python), "--no-deps", "-e", str(project_root)],
        cwd=project_root,
    )
    return venv_python


def _query_python_version(python_executable: Path) -> tuple[int, int]:
    completed = _run(
        [
            str(python_executable),
            "-c",
            "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')",
        ],
        cwd=python_executable.parent,
        capture_output=True,
    )
    raw = (completed.stdout or "").strip()
    return _version_tuple_from_python_spec(raw)


def _run(
    command: Sequence[str],
    *,
    cwd: Path,
    env: dict[str, str] | None = None,
    capture_output: bool = False,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        list(command),
        cwd=str(cwd),
        env=env,
        check=check,
        text=True,
        capture_output=capture_output,
    )


def build_run_tests_invocation(
    *,
    script_path: Path,
    python_executable: str,
    python_spec: str,
    venv_root: str,
    recreate: bool,
    pytest_args: Sequence[str],
) -> list[str]:
    command = [
        python_executable,
        str(script_path),
        "run-tests",
        "--python",
        python_spec,
        "--venv-root",
        venv_root,
    ]
    if recreate:
        command.append("--recreate")
    command.append("--pytest-args")
    command.extend(pytest_args)
    return command


def should_passthrough_run_tests_all_output(
    *,
    show_output: bool,
    runtime_specs: Sequence[str],
) -> bool:
    return show_output and len(runtime_specs) == 1


def report_run_tests_all_results(
    results: Sequence[tuple[str, int, str, str]],
    *,
    show_output: bool,
    stdout: TextIO = sys.stdout,
    stderr: TextIO = sys.stderr,
) -> None:
    for python_spec, returncode, captured_stdout, captured_stderr in results:
        status = "PASS" if returncode == 0 else f"FAIL ({returncode})"
        print(f"{python_spec}: {status}", file=stdout)
        if show_output or returncode != 0:
            if captured_stdout:
                print(f"--- {python_spec} stdout ---", file=stdout)
                print(captured_stdout, end="" if captured_stdout.endswith("\n") else "\n", file=stdout)
            if captured_stderr:
                print(f"--- {python_spec} stderr ---", file=stderr)
                print(captured_stderr, end="" if captured_stderr.endswith("\n") else "\n", file=stderr)


def _python_spec_for_kernel(kernel_tag: str) -> str:
    major, minor = _parse_kernel_tag(kernel_tag)
    return f"{major}.{minor}"


def _parse_kernel_tag(tag: str) -> tuple[int, int]:
    match = _KERNEL_TAG_RE.match(normalize_kernel_tag(tag))
    if match is None:
        raise ValueError(f"Unsupported kernel tag: {tag!r}")
    return int(match.group("major")), int(match.group("minor"))


def _version_tuple_from_python_spec(python_spec: str) -> tuple[int, int]:
    normalized = python_spec.strip()
    if normalized.startswith("v"):
        return _parse_kernel_tag(normalized)
    match = re.search(r"(?P<major>\d+)\.(?P<minor>\d+)", normalized)
    if match is None:
        raise ValueError(f"Unable to derive a major.minor version from {python_spec!r}")
    return int(match.group("major")), int(match.group("minor"))


def _venv_python(venv_dir: Path) -> Path:
    if sys.platform == "win32":
        return venv_dir / "Scripts" / "python.exe"
    return venv_dir / "bin" / "python"


if __name__ == "__main__":
    raise SystemExit(main())
