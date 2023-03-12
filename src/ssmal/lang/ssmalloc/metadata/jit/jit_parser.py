from __future__ import annotations

import ast
from pprint import pprint
import re

from collections import OrderedDict
from dataclasses import is_dataclass
from typing import Any
from types import ModuleType
from ssmal.lang.ssmalloc.metadata.jit.codegen.compiler_error import CompilerError
from ssmal.lang.ssmalloc.metadata.jit.codegen.method_compiler import MethodCompiler
from ssmal.lang.ssmalloc.metadata.jit.strongly_typed_strings import Identifier, TypeName

from ssmal.lang.ssmalloc.metadata.jit.type_info import MethodInfo, TypeInfo


def dump_ast(node: ast.AST, indent=0, prefix=""):
    def _indent(s: Any, marker: str = None):
        # return "    " * indent + f'[{prefix}]\t' + str(s)
        # pf = f'<{prefix}>'
        pf = f"{prefix}"
        _s = str(s)
        padding = max(4, 60 - len(pf)) * " "
        line = f"{pf}{padding}{_s}"
        if marker is not None:
            line = marker + line[len(marker) :]
        return line

    print(_indent(f"> {node.__class__.__name__}", marker=">"))
    for _field in node._fields:
        _prefix = f"{prefix}.{_field}"
        _field_node = getattr(node, _field)
        if isinstance(_field_node, list) and _field_node:
            # dump_ast(_sub_field, indent=indent + 1, prefix=f"{_prefix}[]")
            _array_prefix = f"{_prefix}[{{index}}]"
            _sub_prefix = " " * len(_array_prefix)
            # print(_indent(f"{_field_node}{_prefix}[]"))
            print(_field, end=" > ")
            pprint(_field_node)
            for i, _sub_field in enumerate(_field_node):
                dump_ast(_sub_field, indent=indent + 1, prefix=_array_prefix.format(index=i))
        elif isinstance(_field_node, ast.AST):
            dump_ast(_field_node, prefix=_prefix)
        else:
            print(_indent(f"  {_field} = | {_field_node} | {_field_node.__class__.__name__} |"))
    print(_indent(f"< {node}", marker="<"))


class ParseError(Exception):
    ...


class JitParser:
    type_info_dict: OrderedDict[TypeName, TypeInfo]

    def __init__(self, module: ModuleType) -> None:
        type_name_regex = re.compile(r"[A-Z][a-zA-Z]*")

        self.type_info_dict = OrderedDict[TypeName, TypeInfo]()
        self.type_info_dict[TypeName(Identifier("int"))] = TypeInfo("int", None, int, [], [])
        self.type_info_dict[TypeName(Identifier("str"))] = TypeInfo("str", None, str, [], [])

        for type_name, item in module.__dict__.items():
            if not type_name_regex.match(type_name):
                continue
            if isinstance(item, type) and is_dataclass(item):
                self.type_info_dict[TypeName(Identifier(type_name))] = TypeInfo.from_py_type(item)
            raise CompilerError(item)

        for type_name, type_info in self.type_info_dict.items():
            method_compiler = MethodCompiler(self.type_info_dict, self_type=type_info)
            for method_info in type_info.methods:
                method_info.assembly_code = " ".join(method_compiler.compile_method(method_info))

        # at this point, all methods have their code compiled.
        # Now we just need to assemble the type_info_dict into an executable...

if __name__ == "__main__":
    jit = JitParser(OrderedDict())
    # _get_method_def = jp.get_method_def(JitParser.get_method_def)
    from ssmal.lang.ssmalloc.stdlib.TypeInfo import TypeInfoBase

    method_def = jit.get_method_def(TypeInfoBase.print)
    dump_ast(method_def)
