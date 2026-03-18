from __future__ import annotations

import ast


def build_name(name: str, *, ctx: ast.expr_context = ast.Load()) -> ast.Name:
    return ast.Name(id=name, ctx=ctx)


def build_call(func: ast.expr, *args: ast.expr, **kwargs: ast.expr) -> ast.Call:
    keywords = [ast.keyword(arg=key, value=value) for key, value in kwargs.items()]
    return ast.Call(func=func, args=list(args), keywords=keywords)


def build_dirtyof_call(**dirty_flags: ast.expr) -> ast.Call:
    return build_call(build_name("dirtyof"), **dirty_flags)


def copy_reason_location(node: ast.AST, reason: ast.AST) -> ast.AST:
    return ast.copy_location(node, reason)
