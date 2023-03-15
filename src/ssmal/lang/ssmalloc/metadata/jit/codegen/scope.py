import ast
from collections import OrderedDict
from typing import Generator, Literal
from ssmal.lang.ssmalloc.metadata.jit.codegen.compiler_error import CompilerError
from ssmal.lang.ssmalloc.metadata.jit.codegen.compiler_internals import CompilerInternals
from ssmal.util.writer.line_writer import LineWriter


class Scope:
    """Does not check syntax, does not check types

    Names:
    names are gathered from the args and AnnAssign with Name targets.
    """

    function_def: ast.FunctionDef
    offsets: OrderedDict[str, int]
    locals: set[str]
    args: set[str]
    push_count: int = 0

    ci = CompilerInternals()

    def __init__(self, function_def: ast.FunctionDef) -> None:
        self.function_def = function_def
        self.offsets = OrderedDict[str, int]()
        self.locals = set[str]()
        self.args = set[str]()
        self._parse(self.function_def)

    # fmt: off

    def _check_name(self, name: str, check: Literal['free']) -> None:
        match check:
            case 'free':
                if name in self.offsets: raise CompilerError('fail',check,name, self)
    
    def _add_name(self, name: str, type: Literal['arg', 'local'], check: Literal['free'] = None) -> None:
        if check is not None:
            self._check_name(name, check)
        self.offsets[name] = len(self.offsets)
        if type == 'arg':
            self.args.add(name)
        else:
            self.locals.add(name)

    def _parse(self, node: ast.AST) -> None:
        match node:
            case ast.FunctionDef(args=args, body=body):
                for arg in args.args:
                    self._add_name(arg.arg, 'arg', check='free')
                for stmt in body:
                    self._parse(stmt)
            case ast.AnnAssign(target=ast.Name(id=_id)):
                self._add_name(_id, 'local', check='free')
    

    def push_A(self):
        """
        PSHA, but does bookkeeping so that variable access works properly
        """
        ci = self.ci
        self.push_count += 1
        return ci.PSHA
    
    def pop_A(self):
        """
        POPA, but does bookkeeping so that variable access works properly
        """
        ci = self.ci
        self.push_count -= 1
        return ci.POPA


    def get_offset(self, name: str) -> int:
        return self.offsets[name]
    
    def access_variable(self, line_writer: LineWriter, name: str, mode: Literal['eval', 'access']) -> None:
        """
        CLOBBERS A
        PRESERVES B, STACK

        :param mode:
            'eval'      loads value of variable into register A
            'access'    loads address of variable into register A

        """
        ci = self.ci
        _offset = 4 * (len(self.offsets) - self.offsets[name] + 1)
        _location = "self" if name == 'self' else 'local' if name in self.locals else 'arg'
        line_writer.indent()
        line_writer.write_line(ci.COMMENT(f'[access {_location}] {name} {mode=}'))
        line_writer.write_line(ci.PUSH_B(), ci.MOVSA, ci.SUBi, f'{_offset}')
        if mode == 'eval':
            line_writer.write_line(ci.FOLLOW_A(), ci.COMMENT('eval'))
        line_writer.write_line(ci.POP_B())
        line_writer.dedent()


# fmt: on
