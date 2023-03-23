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

    heap_start_label: str
    label_maker: LabelMaker
    string_table: StringTable
    type_dict: OrderedDict[TypeName, TypeInfo]

    _i: int = 0

    def __init__(self, string_table: StringTable, type_dict: OrderedDict[TypeName, TypeInfo], label_maker: LabelMaker) -> None:
        self.label_maker = label_maker
        self.string_table = string_table
        self.type_dict = type_dict

        self.heap_start_label = self.label_maker.get_label_from_name("HEAP_START")
        self.allocate_label = "allocator.malloc"

    def create_heap(self, w: LineWriter, size=0x400) -> None:
        ci = self.ci
        _start = self.heap_start_label

        # start:        current_offset (heap_start + current_offset === first_available)
        # start+0x20:   heap_start (=== start + 0x20)
        # start+size:   heap_end / Allocation function
        # ...:          die (HALT)
        w.write_line(".align", ci.ZSTR("HEAP START"), ".align")
        w.write_line(ci.MARK_LABEL(_start), ".zeros", f"0x{size + 0x20:04x}")
        w.write_line(".align", ci.ZSTR("HEAP END"), ".align")

        die_label = self.label_maker.get_label_from_name("die")
        w.write_line(ci.MARK_LABEL(self.allocate_label), ci.COMMENT("Allocation function"))
        # assume A holds size we need to allocate
        # need to increment current_offset, A <- start + 0x20 + current_offset
        # stack: ret
        w.write_line(ci.PSHA, ci.LDAi, ci.GOTO_LABEL(_start), ci.SWPAB, ci.LDAb, ci.COMMENT("Current index"))
        # stack: ret, size
        w.write_line(ci.SWPAB, ci.LDAi, ci.GOTO_LABEL(_start), ci.ADDi, "0x20", ci.ADDB, ci.PSHA, ci.COMMENT("return value (pointer)"))
        # stack: ret, size, result
        w.write_line(ci.POPA, ci.SWPAB, ci.POPA, ci.SWPAB, ci.PSHA, ci.SWPAB, ci.PSHA, ci.COMMENT("Rotate top of stack"))
        # stack: ret, (B=)result, (A=)size
        w.write_line(ci.LDAi, ci.GOTO_LABEL(_start), ci.SWPAB, ci.LDAb, ci.COMMENT("Current offset"))
        w.write_line(ci.SWPAB, ci.POPA, ci.ADDB, ci.PSHA, ci.COMMENT("New offset"))
        # stack: ret, result, (A=)new_offset
        w.write_line(ci.SUBi, f"{size:x}", ci.MULi, "-1", ci.BRNi, ci.GOTO_LABEL(die_label), ci.COMMENT("die if too big"))
        w.write_line(ci.LDAi, ci.GOTO_LABEL(_start), ci.SWPAB, ci.POPA, ci.STAb, ci.COMMENT("save new index"))
        # stack: ret, result
        w.write_line(ci.POPA, ci.RETN, ci.COMMENT("return, A <- pointer"))

        w.write_line(ci.MARK_LABEL(die_label), ci.HALT)
