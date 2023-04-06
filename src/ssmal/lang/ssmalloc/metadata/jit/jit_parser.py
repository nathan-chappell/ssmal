from __future__ import annotations

import ast
import re
import sys

from pprint import pprint

from collections import OrderedDict
from dataclasses import is_dataclass
from typing import Any, Generator
from types import ModuleType
from ssmal.assemblers.assembler import Assembler
from ssmal.assemblers.tokenizer import tokenize
from ssmal.components.registers import Registers
from ssmal.lang.ssmalloc.metadata.jit.codegen.allocator import TrivialAllocator
from ssmal.lang.ssmalloc.metadata.jit.codegen.compiler_error import CompilerError
from ssmal.lang.ssmalloc.metadata.jit.codegen.compiler_internals import CompilerInternals
from ssmal.lang.ssmalloc.metadata.jit.codegen.label_maker import LabelMaker
from ssmal.lang.ssmalloc.metadata.jit.codegen.method_compiler import MethodCompiler
from ssmal.lang.ssmalloc.metadata.jit.codegen.string_table import StringTable
from ssmal.lang.ssmalloc.metadata.jit.strongly_typed_strings import Identifier, TypeName

from ssmal.lang.ssmalloc.metadata.jit.type_info import MethodInfo, TypeInfo, int_type, str_type
from ssmal.processors.processor import Processor
from ssmal.util.writer.line_writer import LineWriter
from ssmal.vm1.sys_io import SysIO


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
    ci = CompilerInternals()
    type_name_regex = re.compile(r"[A-Z][a-zA-Z]*")

    allocator: TrivialAllocator
    label_maker: LabelMaker
    string_table: StringTable
    type_info_dict: OrderedDict[TypeName, TypeInfo]

    # pipeline...
    debug_info: str | None = None
    line_writer: LineWriter | None
    assembly: bytes | None
    processor: Processor | None

    INITAL_SP_OFFSET = 0x10
    heap_start_addr: int | None = None
    heap_size = 0x200

    def __init__(self) -> None:
        self.label_maker = LabelMaker()
        self.string_table = StringTable()
        self.type_info_dict = TypeInfo.builtin_type_info()

        self.allocator = TrivialAllocator(string_table=self.string_table, type_dict=self.type_info_dict, label_maker=self.label_maker)

        self.assembly = None
        self.line_writer = None
        self.processor = None

    def parse_module(self, module: ModuleType, do_compile=True):
        for type_name, item in module.__dict__.items():
            if not self.type_name_regex.match(type_name):
                continue
            elif isinstance(item, type) and is_dataclass(item):
                self.type_info_dict[TypeName(Identifier(type_name))] = TypeInfo.from_py_type(item)
            else:
                raise CompilerError(item)

        for type_name, type_info in self.type_info_dict.items():
            for method_info in type_info.methods:
                line_writer = LineWriter()
                method_compiler = MethodCompiler(
                    line_writer,
                    self.type_info_dict,
                    self_type=type_info,
                    string_table=self.string_table,
                    label_maker=self.label_maker,
                    allocator=self.allocator,
                )
                method_compiler.compile_method(method_info)
                method_info.assembly_code = method_compiler.line_writer.text

        # at this point, all methods have their code compiled.
        # Now we just need to assemble the type_info_dict into an executable...

        if do_compile:
            self.compile()

    def compile(self, do_assemble=True) -> None:
        # We assume:
        #   IP is 0
        #   SP is after the HEAP_END symbol
        ci = self.ci
        w = self.line_writer = LineWriter()

        # INITAL_SP_OFFSET = self.INITAL_SP_OFFSET
        EXIT_OFFSET = 0x20
        TYPEINFO_OFFSET = 0x40
        ENTRYPOINT = "Program.main"
        # INITIAL_SP = "INITIAL_SP"
        # create assembly...

        w.write_line(".goto 0", ci.POPA, ci.LDAi, f"0x{EXIT_OFFSET:02x}", ci.PSHA, ci.BRi, ci.GOTO_LABEL(ENTRYPOINT), ci.COMMENT("start"))
        w.write_line(f".goto 0x{EXIT_OFFSET:02x}", ci.HALT, ci.COMMENT("exit"))
        # it's pointless to try to get the initial_sp directly from the assembler...
        # w.write_line(f".goto 0x{INITAL_SP_OFFSET:02x}", INITIAL_SP, ci.COMMENT("Initial SP"))
        w.write_line(f".goto 0x{TYPEINFO_OFFSET:02x}", ci.ZSTR("TYPEINFO"), f".align")

        # vtables
        for type_name, type_info in self.type_info_dict.items():
            w.write_line(ci.ZSTR(type_name), ".align")
            w.write_line(ci.MARK_LABEL(f"{type_name}.vtable"))
            w.indent()
            for method_info in type_info.methods:
                w.write_line(ci.GOTO_LABEL(method_info.implementation_symbol))
            w.write_line(".align")
            w.dedent()

        # method implementations
        for type_name, type_info in self.type_info_dict.items():
            w.write_line(ci.ZSTR(type_name), ".align")
            w.write_line(ci.MARK_LABEL(f"{type_name}.methods"))
            w.indent()
            for method_info in type_info.methods:
                assert isinstance(method_info.parent, TypeInfo)
                if method_info.parent.name != type_info.name:
                    # implemented by someone else
                    continue
                if method_info.assembly_code is None:
                    raise CompilerError(method_info)
                w.write_line(ci.MARK_LABEL(method_info.implementation_symbol))
                w.indent()
                for line in method_info.assembly_code.split("\n"):
                    w.write_line(line)
                w.write_line(".align")
                w.dedent()
            w.dedent()

        self.string_table.compile(w)
        self.allocator.create_heap(w, self.heap_size)
        w.write_line(".zeros 0x20", ".align", ci.COMMENT("a little space before stack."))

        if do_assemble:
            self.assemble()

    def assemble(self, do_initialize_processor=True):
        if self.line_writer is None:
            raise CompilerError(f"You must first compile before assembling.")

        text = self.line_writer.text
        print(text)
        tokens = list(tokenize(text))
        assembler = Assembler(tokens)
        assembler.assemble()
        assembly = bytearray(assembler.buffer.getvalue())
        self.heap_start_addr = assembler.labels["label_name_HEAP_START__0"].address
        assembly[self.INITAL_SP_OFFSET : self.INITAL_SP_OFFSET + 4] = len(assembly).to_bytes(4, "little", signed=True)
        self.assembly = bytes(assembly)
        self.debug_info = assembler.debug_info

        if do_initialize_processor:
            self.initialize_processor()

    def initialize_processor(self):
        if self.assembly is None:
            raise CompilerError(f"You must first assemble before initializing.")
        assert self.heap_start_addr is not None
        processor = Processor()
        processor.memory.store_bytes(0, self.assembly)
        initial_sp = processor.memory.load(self.INITAL_SP_OFFSET)
        processor.registers.SP = initial_sp
        processor.memory.monitor(0, self.heap_start_addr)
        sys_io = SysIO()
        sys_io.bind(sys.stdin, sys.stdout)
        processor.sys_vector = sys_io.sys_vector
        self.processor = processor
