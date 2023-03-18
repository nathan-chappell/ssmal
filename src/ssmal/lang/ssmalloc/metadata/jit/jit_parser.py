from __future__ import annotations

import ast
from pprint import pprint
import re

from collections import OrderedDict
from dataclasses import is_dataclass
from typing import Any, Generator
from types import ModuleType
from ssmal.lang.ssmalloc.metadata.jit.codegen.compiler_error import CompilerError
from ssmal.lang.ssmalloc.metadata.jit.codegen.compiler_internals import CompilerInternals
from ssmal.lang.ssmalloc.metadata.jit.codegen.method_compiler import MethodCompiler
from ssmal.lang.ssmalloc.metadata.jit.codegen.string_table import StringTable
from ssmal.lang.ssmalloc.metadata.jit.strongly_typed_strings import Identifier, TypeName

from ssmal.lang.ssmalloc.metadata.jit.type_info import MethodInfo, TypeInfo, int_type, str_type
from ssmal.util.writer.line_writer import LineWriter


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
    string_table: StringTable
    type_info_dict: OrderedDict[TypeName, TypeInfo]
    ci = CompilerInternals()
    type_name_regex = re.compile(r"[A-Z][a-zA-Z]*")

    def __init__(self) -> None:
        self.string_table = StringTable(0x400)
        self.type_info_dict = TypeInfo.builtin_type_info()
    
    def parse_module(self, module: ModuleType):
        for type_name, item in module.__dict__.items():
            if not self.type_name_regex.match(type_name):
                continue
            if isinstance(item, type) and is_dataclass(item):
                self.type_info_dict[TypeName(Identifier(type_name))] = TypeInfo.from_py_type(item)
            raise CompilerError(item)

        for type_name, type_info in self.type_info_dict.items():
            for method_info in type_info.methods:
                line_writer = LineWriter()
                method_compiler = MethodCompiler(line_writer, self.type_info_dict, self_type=type_info, string_table=self.string_table)
                method_compiler.compile_method(method_info)
                method_info.assembly_code = method_compiler.line_writer.text

        # at this point, all methods have their code compiled.
        # Now we just need to assemble the type_info_dict into an executable...

    def get_type_info_binary(self, offset: int) -> tuple[bytes, OrderedDict[str, int]]:
        ...

    def compile(self, line_writer: LineWriter) -> Generator[str, None, None]:
        # We assume:
        #   IP is 0
        #   SP is after the HEAP_END symbol
        ci = self.ci
        TYPEINFO_OFFSET = 0x20
        ENTRYPOINT = "Program.Main"
        # create assembly...
        type_info_binary, type_info_labels = self.get_type_info_binary(TYPEINFO_OFFSET)

        yield ".goto 0"
        yield ci.BRi
        yield ci.GOTO_LABEL(ENTRYPOINT)
        yield ".goto 0x20"
        yield '"TYPEINFO"'
        yield f".goto 0x{TYPEINFO_OFFSET:02x}"
        yield f"b'{type_info_binary.hex()}"
        for symbol, address in type_info_labels.items():
            yield ci.MARK_LABEL(symbol)
            yield f"0x{address:08x}"
        yield ".align"
        for type_info in self.type_info_dict.values():
            for method_info in type_info.methods:
                yield ci.MARK_LABEL(f"{type_info.name}.{method_info.name}")
                if method_info.assembly_code is None:
                    raise CompilerError(method_info)
                yield method_info.assembly_code
                yield ".align"
