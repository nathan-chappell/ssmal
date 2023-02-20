from typing import List, Dict, Set, cast
import io

from processors.opcodes import reverse_opcode_map
from assemblers.token import Token


class Assembler:
    byteorder: str = "little"
    encoding: str = "ascii"

    buffer: io.BytesIO
    debug_info: Dict[int, Token]
    included_files: Set[str]
    symbol_table: Dict[str, bytes]
    tokens: List[Token]

    _index: int

    def __init__(self, tokens: List[Token]):
        self.buffer = io.BytesIO()
        self.debug_info = {}
        self.symbol_table = dict(reverse_opcode_map)
        self.tokens = tokens
        self._index = 0

    @property
    def current_position(self) -> int:
        return self.buffer.tell()

    @property
    def eat_token(self) -> Token:
        token = self.tokens[self._index]
        self._index += 1
        return token

    def _write(self, _bytes: bytes, token: Token):
        self.buffer.write(_bytes)
        for i in range(len(_bytes)):
            self.debug_info[self.current_position + i] = token

    def assemble(self):
        while self._index < len(self.tokens):
            self.advance()

    def advance(self):
        token = self.eat_token

        if token.type == "id":
            self._write(self.symbol_table[self.get_id(token)], token)
        elif token.type == "xint":
            self._write(self.get_bytes(token), token)
        elif token.type == "dint":
            self._write(self.get_bytes(token), token)
        elif token.type == "bstr":
            self._write(self.get_bytes(token), token)
        elif token.type == "zstr":
            self._write(self.get_bytes(token), token)
        elif token.type == "comment":
            pass
        elif token.type == "ws":
            pass
        elif token.type == "dir":
            self.handle_directive(token)
        else:
            raise NotImplementedError()

    def handle_directive(self, t0: Token):
        if t0.value == ".here":
            self._write(self.current_position.to_bytes(4, "little"), t0)
        else:
            t1 = self.eat_token
            if t0.value == ".byteorder":
                self.byteorder = self.get_value(t1)  # type: ignore
            elif t0.value == ".encoding":
                self.encoding = self.get_value(t1)  # type: ignore
            elif t0.value == ".goto":
                self.buffer.seek(self.get_value(t1))  # type: ignore
            else:
                t2 = self.eat_token
                if t0.value == ".def":
                    self.symbol_table[self.get_id(t1)] = self.get_bytes(t2)
                elif t0.value == ".repeat":
                    self._write(cast(int, self.get_value(t1)) * self.get_bytes(t2), t0)
                else:
                    raise NotImplementedError()

    def get_bytes(self, token: Token) -> bytes:
        if token.type == "xint":
            return int(token.value, 16).to_bytes(4, self.byteorder)  # type: ignore
        elif token.type == "dint":
            return int(token.value).to_bytes(4, self.byteorder)  # type: ignore
        elif token.type == "bstr":
            return bytes.fromhex(token.value[1:-1])
        elif token.type == "zstr":
            return bytes(token.value[1:-1], self.encoding) + b"\x00"
        else:
            raise NotImplementedError()

    def get_value(self, token: Token) -> int | str | bytes:
        if token.type == "xint":
            return int(token.value, 16)
        elif token.type == "dint":
            return int(token.value)
        elif token.type == "bstr":
            return bytes(token.value[1:-1], self.encoding)
        elif token.type == "zstr":
            return token.value[1:-1]
        elif token.type == "id":
            return self.symbol_table[token.value]
        else:
            raise NotImplementedError()

    def get_id(self, token: Token) -> str:
        if token.type == "id":
            return token.value
        raise Exception(f"Expected id at {token}")