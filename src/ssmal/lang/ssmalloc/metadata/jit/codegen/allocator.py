from __future__ import annotations

from collections import OrderedDict
from ssmal.lang.ssmalloc.metadata.jit.codegen.label_maker import LabelMaker
from ssmal.lang.ssmalloc.metadata.jit.codegen.string_table import StringTable
from ssmal.lang.ssmalloc.metadata.jit.strongly_typed_strings import TypeName

from ssmal.util.writer.line_writer import LineWriter

from ssmal.lang.ssmalloc.metadata.jit.codegen.compiler_internals import CompilerInternals
from ssmal.lang.ssmalloc.metadata.jit.type_info import TypeInfo


class TrivialAllocator:
    ci = CompilerInternals()

    heap_label: str
    label_maker: LabelMaker
    line_writer: LineWriter
    string_table: StringTable
    type_dict: OrderedDict[TypeName, TypeInfo]

    _i: int = 0

    def __init__(
        self, assembler_writer: LineWriter, string_table: StringTable, type_dict: OrderedDict[TypeName, TypeInfo], label_maker: LabelMaker
    ) -> None:
        self.label_maker = label_maker
        self.line_writer = assembler_writer
        self.string_table = string_table
        self.type_dict = type_dict

        self.heap_label = self.label_maker.get_label_from_name("HEAP_START")
        self.allocate_label = self.label_maker.get_label_from_name("allocate")

    def create_heap(self, size=0x400) -> None:
        ci = self.ci
        w = self.line_writer

        w.write_line(".align", ci.ZSTR("HEAP START"), ".align")
        w.write_line(ci.MARK_LABEL(self.heap_label), ".zeros", f"{size + 0x20:x}")
        w.write_line(".align", ci.ZSTR("HEAP END"), ".align")

        die_label = self.label_maker.get_label_from_name("die")
        w.write_line(ci.MARK_LABEL(self.allocate_label), ci.COMMENT("Allocation function"))
        # assume A holds size we need to allocate
        w.write_line(ci.PSHA, ci.LDAi, ci.GOTO_LABEL(self.heap_label), ci.COMMENT("Current index"))
        w.write_line(ci.SWPAB, ci.POPA, ci.ADDB, ci.PSHA, ci.COMMENT("Calculate new index"))
        w.write_line(ci.SUBi, f"{size:x}", ci.BRNi, ci.GOTO_LABEL(die_label))
        w.write_line(ci.LDAi, ci.GOTO_LABEL(self.heap_label), ci.SWPAB, ci.POPA, ci.STAb, ci.COMMENT("save new index"))

        w.write_line(ci.MARK_LABEL(die_label), ci.HALT)
