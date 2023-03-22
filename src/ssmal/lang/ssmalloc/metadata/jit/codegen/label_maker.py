import ast


class LabelMaker:
    _i: int = 0

    def get_label_from_expr(self, expr: ast.expr) -> str:
        label = f"label_for_line_{expr.lineno}_col_{expr.col_offset}__{self._i}"
        self._i += 1
        return label

    def get_label_from_name(self, name: str) -> str:
        label = f"label_name_{name}__{self._i}"
        self._i += 1
        return label
