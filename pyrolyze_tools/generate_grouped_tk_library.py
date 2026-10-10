"""Offline grouped Tk generation; promotion requires exclusive maintenance."""

from __future__ import annotations

from collections.abc import Sequence

from pyrolyze_tools.generate_grouped_native_command import main as generate_grouped


def main(argv: Sequence[str] | None = None) -> int:
    return generate_grouped(argv, root_module="tkinter",
                            command_module="pyrolyze_tools.generate_grouped_tk_library")


if __name__ == "__main__":
    raise SystemExit(main())
