import ast
import inspect
import textwrap

from collections import OrderedDict
from typing import Any, Callable

from ssmal.lang.ssmalloc.metadata.type_info import TypeInfo


class JitParser:
    type_cache: OrderedDict[str, TypeInfo]

    def __init__(self, type_cache: OrderedDict[str, TypeInfo]) -> None:
        self.type_cache = type_cache

    def get_method_def(self, method_def: Callable) -> ast.FunctionDef:
        _module = ast.parse(textwrap.dedent(inspect.getsource(method_def)))
        _function_def = _module.body[0]
        if not isinstance(_function_def, ast.FunctionDef):
            raise Exception(f"Invalid method def: {method_def}", method_def)

        return _function_def

    def dump_ast(self, node: ast.AST, indent=0, prefix=""):
        def _indent(s: Any):
            # return "    " * indent + f'[{prefix}]\t' + str(s)
            # pf = f'<{prefix}>'
            pf = f'{prefix}'
            _s = str(s)
            padding = max(4, 60 - len(pf)) * ' '
            return f'{pf}{padding}{_s}'

        print(_indent(f'> {node}'))
        for _field in node._fields:
            _prefix = f"{prefix}.{_field}"
            _field_node = getattr(node, _field)
            if isinstance(_field_node, list):
                for _sub_field in _field_node:
                    self.dump_ast(_sub_field, indent=indent + 1, prefix=f'{_prefix}[]')
            elif isinstance(_field_node, ast.AST):
                self.dump_ast(_field_node, prefix=_prefix)
            else:
                print(_indent(f'"{_field_node}"'))


if __name__ == "__main__":
    jp = JitParser(OrderedDict())
    _get_method_def = jp.get_method_def(JitParser.get_method_def)
    jp.dump_ast(_get_method_def)
