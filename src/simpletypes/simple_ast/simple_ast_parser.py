from dataclasses import dataclass
from pathlib import Path
import ast
import typing as T

import simpletypes.simple_ast.simple_ast_nodes as N


def _get_ast(filename: str | Path):
    with open(filename, "r") as f:
        return compile(f.read(), str(filename), "exec", ast.PyCF_ONLY_AST)


def _get_name_or_constant_str(node: ast.Constant | ast.Name | ast.expr | None) -> str:
    # fmt: off
    match node:
        case ast.Name:      return node.id
        case ast.Constant:  return str(node.value)
        case _: raise NotImplementedError(node)
    # fmt: on


def _get_type(node: T.Any) -> str:
    ...


def parse_CallExpr(call: ast.Call) -> N.CallExpr:
    ...


def parse_AssignmentStmt(ann_assign: ast.AnnAssign) -> N.Statement:
    value: str | N.CallExpr
    # fmt: off
    match ann_assign.value:
        case ast.Name():        value = _get_name_or_constant_str(ann_assign.value)
        case ast.Constant():    value = _get_name_or_constant_str(ann_assign.value)
        case ast.Call():        value = parse_CallExpr(ann_assign.value)
        case _: raise NotImplementedError(ann_assign)
    # fmt: on
    name = _get_name_or_constant_str(ann_assign.target)
    return N.AssignmentStmt(name, value)


def parse_ClassDef(class_def: ast.ClassDef) -> N.Statement:
    name = class_def.name
    bases = tuple(_get_name_or_constant_str(base) for base in class_def.bases)
    return N.ClassDef(name, bases)


def parse_FunctionDef(function_def: ast.FunctionDef) -> N.Statement:
    parameter_types = tuple(_get_name_or_constant_str(arg.annotation) for arg in function_def.args.args)
    return_type = _get_name_or_constant_str(function_def.returns)
    return N.FunctionDef(parameter_types, return_type)


def parse_VariableDef(ann_assign: ast.AnnAssign) -> N.Statement:
    type_name = _get_name_or_constant_str(ann_assign.annotation)
    name = _get_name_or_constant_str(ann_assign.target)
    return N.VariableDef(name, type_name)


def parse_Program(module: ast.Module):
    body: list[N.Statement] = []
    # fmt: off
    for node in module.body:
        match node:
            case ast.AnnAssign(value=None): body.append(parse_VariableDef(node))
            case ast.AnnAssign():           body.append(parse_AssignmentStmt(node))
            case ast.ClassDef():            body.append(parse_ClassDef(node))
            case ast.FunctionDef():         body.append(parse_FunctionDef(node))
            case _: raise NotImplementedError(node)
    # fmt: on
