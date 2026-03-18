from __future__ import annotations

import ast


class PyRolyzeCompileError(RuntimeError):
    """Compile-time error with stable code and source-location metadata."""

    def __init__(
        self,
        message: str,
        *,
        code: str = "PYR-E-COMPILE",
        path: str | None = None,
        line: int | None = None,
        column: int | None = None,
        node_class: str | None = None,
        suggested_fix: str | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.path = path
        self.line = line
        self.column = column
        self.node_class = node_class
        self.suggested_fix = suggested_fix


def error_from_node(
    node: ast.AST,
    *,
    code: str,
    message: str,
    module_name: str,
    suggested_fix: str | None = None,
) -> PyRolyzeCompileError:
    return PyRolyzeCompileError(
        message,
        code=code,
        path=module_name,
        line=getattr(node, "lineno", None),
        column=getattr(node, "col_offset", None),
        node_class=node.__class__.__name__,
        suggested_fix=suggested_fix,
    )
