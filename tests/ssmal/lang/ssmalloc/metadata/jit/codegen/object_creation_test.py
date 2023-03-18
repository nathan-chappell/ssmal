import ast
from collections import OrderedDict
from dataclasses import dataclass
import inspect
import textwrap

import pytest

from ssmal.assemblers.tokenizer import tokenize
from ssmal.assemblers.assembler import Assembler
from ssmal.components.memory import MonitoredWrite
from ssmal.instructions.processor_signals import HaltSignal
from ssmal.lang.ssmalloc.metadata.jit.jit_parser import JitParser
from ssmal.lang.ssmalloc.metadata.jit.strongly_typed_strings import Identifier, TypeName
from ssmal.processors.processor import Processor

from ssmal.lang.ssmalloc.metadata.jit.type_info import TypeInfo, int_type, str_type
from ssmal.lang.ssmalloc.metadata.jit.codegen.scope import Scope
from ssmal.lang.ssmalloc.metadata.jit.codegen.method_compiler import MethodCompiler
from ssmal.util.writer.line_writer import LineWriter
import tests.ssmal.lang.ssmalloc.metadata.jit.codegen.samples.pair as pair_module


def test_object_creation():
    jit_parser = JitParser()
    jit_parser.parse_module(pair_module)
