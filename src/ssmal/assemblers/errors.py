from ssmal.assemblers.label import Label
from ssmal.assemblers.token import Token


class AssemblerError(Exception):
    ...


class UnexpectedTokenError(AssemblerError):
    expected: str
    token: Token

    def __init__(self, token: Token, expected: str):
        self.expected = expected
        self.token = token
        super().__init__(f"Unexpected token: {self.token} (expected: {self.expected})")


class UnresolvedLabelError(AssemblerError):
    label: Label

    def __init__(self, label: Label):
        self.label = label
        super().__init__(f"Unresolved label: {label.token}")
