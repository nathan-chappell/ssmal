from dataclasses import dataclass
from pathlib import Path
import ast
import typing as T

import simpletypes.simple_ast.simple_ast_nodes as N


def _get_identifier(node: ast.Name | None) -> N.Identifier:
    # fmt: off
    match node:
        # case ast.Name():      return N.IdentifierExpr(T.cast(N.Identifier, node.id))
        case ast.Name():      return T.cast(N.Identifier, node.id)
        case _: raise UnexpectedNode(node)
    # fmt: on


def _get_typename(node: ast.Constant | ast.Name | ast.expr | None) -> N.TypeName:
    typename: str
    # fmt: off
    match node:
        case ast.Constant():
            match node.value:
                case str(): typename = node.value
                case None: typename = 'None'
                case _: raise UnexpectedNode(node, 'must supply string for type constants')
        case ast.Name(): typename = _get_identifier(node)
        case _: raise UnexpectedNode(node)
    # fmt: on
    return T.cast(N.TypeName, typename)


def _get_value(node: ast.Constant) -> N.ValueExpr:
    if isinstance(node.value, int | str):
        return N.ValueExpr(node.value)
    raise UnexpectedNode(node, "const must be int | str")


class ParseException(Exception):
    ...


class UnexpectedNode(ParseException):
    ...


def parse_CallExpr(call: ast.Call) -> N.CallExpr:
    # fmt: off
    match call.func:
        case ast.Name():        function_name = _get_identifier(call.func)
        case _: raise UnexpectedNode(call)
    # fmt: on

    arguments = [parse_Expression(arg) for arg in call.args]

    return N.CallExpr(function_name, arguments)


def parse_Expression(expr: ast.expr) -> N.Expression:
    # fmt: off
    match expr:
        case ast.Name():        return N.IdentifierExpr(_get_identifier(expr))
        case ast.Constant():    return _get_value(expr)
        case ast.Call():        return parse_CallExpr(expr)
        case _: raise UnexpectedNode(expr)
    # fmt: on


def parse_AssignmentStmt(ann_assign: ast.Assign) -> N.Statement:
    if len(ann_assign.targets) > 1:
        raise UnexpectedNode(ann_assign, "multiple targets in assignment not allowed")
    target = ann_assign.targets[0]
    value = parse_Expression(ann_assign.value)
    # fmt: off
    match target:
        case ast.Name():        return N.AssignmentStmt(_get_identifier(target), value)
        case _: raise UnexpectedNode(ann_assign)
    # fmt: on


def parse_ClassDef(class_def: ast.ClassDef) -> N.Statement:
    name = T.cast(N.TypeName, class_def.name)
    bases = list(_get_typename(base) for base in class_def.bases)
    return N.ClassDef(name, bases)


def parse_FunctionDef(function_def: ast.FunctionDef) -> N.Statement:
    parameter_types = list(_get_typename(arg.annotation) for arg in function_def.args.args)
    return_type = _get_typename(function_def.returns)
    return N.FunctionDef(parameter_types, return_type)


def parse_VariableDef(ann_assign: ast.AnnAssign) -> N.Statement:
    if ann_assign.value is not None:
        raise UnexpectedNode(ann_assign, "variables cannot be initialized and declared at the same time")
    type_name = _get_typename(ann_assign.annotation)
    # fmt: off
    match ann_assign.target:
        case ast.Name(): return N.VariableDef(_get_identifier(ann_assign.target), type_name)
        case _: raise UnexpectedNode(ann_assign)
    # fmt: on


# def parse_TypeAlias(ann_assign: ast.AnnAssign) -> N.Statement:
# Maybe in the future...


def parse_Program(module: ast.Module) -> N.Program:
    body: list[N.Statement] = []
    # fmt: off
    for node in module.body:
        match node:
            case ast.AnnAssign(value=None): body.append(parse_VariableDef(node))
            # case ast.AnnAssign(annotation=ast.Name(id='type')): body.append(parse_TypeAlias(node))
            case ast.Assign():              body.append(parse_AssignmentStmt(node))
            case ast.ClassDef():            body.append(parse_ClassDef(node))
            case ast.FunctionDef():         body.append(parse_FunctionDef(node))
            case _: raise UnexpectedNode(node, 'check your grammar')
    # fmt: on
    return N.Program(body)


# TODO: module interaface...

if __name__ == "__main__":  # pragma: no cover
    import argparse
    import pprint
    import sys

    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument("filename")

    args = argument_parser.parse_args(sys.argv[1:])
    with open(args.filename) as f:
        source_code = f.read()
        program = parse_Program(compile(source_code, args.filename, "exec", ast.PyCF_ONLY_AST))
        pprint.pprint(program)
