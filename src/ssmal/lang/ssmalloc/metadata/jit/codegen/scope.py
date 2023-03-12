import ast
from collections import OrderedDict
from typing import Generator, Literal
from ssmal.lang.ssmalloc.metadata.jit.codegen.compiler_error import CompilerError
from ssmal.lang.ssmalloc.metadata.jit.codegen.compiler_internals import CompilerInternals


class Scope:
    """Does not check syntax, does not check types

    Names:
    names are gathered from the args and AnnAssign with Name targets.
    """

    function_def: ast.FunctionDef
    offsets: OrderedDict[str, int]
    locals: set[str]
    args: set[str]

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
                    self._add_name(arg.arg, 'local', check='free')
                for stmt in body:
                    self._parse(stmt)
            case ast.AnnAssign(target=ast.Name(id=_id)):
                self._add_name(_id, 'local', check='free')


    def get_offset(self, name: str) -> int:
        return self.offsets[name]
    
    def access_variable(self, name: str, mode: Literal['eval', 'access']) -> Generator[str, None, None]:
        ci = self.ci
        # 'eval':   loads value of variable into register A
        # 'access': loads address of variable into register A
        # save B
        yield ci.SWPAB; yield ci.PSHA; yield ci.SWPAB
        # load SP into A
        yield ci.MOVSA
        # offset is from bottom, and currenty SP is at TOP + 4 (because we saved B)
        _offset = 4 * (len(self.offsets) - self.offsets[name] + 1)
        yield ci.SUBi; yield f'{_offset}'; 
        # now A points at variable
        if mode == 'eval':
            yield ci.SWPAB; yield ci.LDAb
        # restore B
        yield ci.SWPAB; yield ci.POPA; yield ci.SWPAB


# fmt: on
