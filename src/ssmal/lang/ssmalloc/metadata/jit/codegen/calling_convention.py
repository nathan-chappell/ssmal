import ast
from typing import Callable, Generator, Literal
from ssmal.lang.ssmalloc.metadata.jit.codegen.compiler_error import CompilerError
from ssmal.lang.ssmalloc.metadata.jit.codegen.compiler_internals import CompilerInternals
from ssmal.lang.ssmalloc.metadata.jit.codegen.scope import Scope

TEvaluateCallback = Callable[[ast.expr, Literal["access", "eval"]], Generator[str, None, None]]


# fmt: off

class CallingConvention:
    ci = CompilerInternals()
    evaluate: TEvaluateCallback
    scope: Scope

    def __init__(self, evaluate_callback: TEvaluateCallback, scope: Scope) -> None:
        self.evaluate = evaluate_callback
        self.scope = scope


    def call_method(self, func_expr: ast.expr, args_exprs: list[ast.expr]) -> Generator[str, None, None]:
        ci = self.ci
        # stack:
        # ret, method, self, TOP
        #                    ^ ^
        #                    B,SP
        # save return address
        yield ci.SWPAI; ci.PSHA; yield ci.SWPAI
        # B points to bottom of stack
        yield ci.SWPAS; yield ci.PSHA; yield ci.SWPAS; yield ci.POPA; yield ci.SWPAB
        # push all arguments onto stack
        for arg_expr in args_exprs:
            yield from self.evaluate(arg_expr, 'eval'); yield ci.PSHA
        # stack:
        # ret, self, arg1, arg2, ..., argn, TOP
        #      ^                             ^
        #      B                            SP
        # registers:
        # B = &args[0]

        yield from self.evaluate(func_expr, 'eval'); yield ci.BRa

    def _copy_SP_to_A(self) -> Generator[str, None, None]:
        ci = self.ci
        yield ci.SWPAS; yield ci.PSHA; yield ci.SWPAS; yield ci.POPA;
    
    def answer_method(self) -> Generator[str, None, None]:
        ci = self.ci
        # initialize locals with 0
        yield ci.LDAi; yield "0"
        yield from (ci.PSHA for _ in range(len(self.scope.locals)))

    def return_(self) -> Generator[str, None, None]:
        ci = self.ci
        # pop entire stack
        yield from (ci.POPA for _ in range(len(self.scope.locals)))
        yield from (ci.POPA for _ in range(len(self.scope.args)))
        # return
        yield ci.POPA; ci.SWPAI
