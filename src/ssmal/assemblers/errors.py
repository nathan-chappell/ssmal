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
