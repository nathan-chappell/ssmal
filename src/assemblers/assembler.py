from typing import List, Dict
import io

from processors.opcodes import reverse_opcode_map
from assemblers.token import Token


class Assembler:
    byteorder: str = "little"
    encoding: str = "ascii"

    buffer: io.BytesIO
    debug_info: Dict[int, Token]
    symbol_table: Dict[str, bytes]

    def __init__(self):
        self.buffer = io.BytesIO()
        self.debug_info = {}
        self.symbol_table = dict(reverse_opcode_map)

    @property
    def current_position(self) -> int:
        return self.buffer.tell()
    
    def _write(self, _bytes: bytes, token: Token):
        self.buffer.write(_bytes)
        for i in range(len(_bytes)):
            self.debug_info[self.current_position + i] = token

    def assemble(self, tokens: List[Token]):
        i = 0

        while i < len(tokens):
            token = tokens[i]
            if token.type == "id":
                self._write(self.symbol_table[self.get_id(token)], token)
            elif token.type == "dir":
                if token.value == ".here":
                    self._write(self.current_position.to_bytes(4, "little"), token)
                    i += 1
                    continue
                elif token.value == ".byteorder":
                    self.byteorder = self.get_value(tokens[i + 1]) # type: ignore
                    i += 2
                    continue
                elif token.value == ".encoding":
                    self.encoding = self.get_value(tokens[i + 1]) # type: ignore
                    i += 2
                    continue
                elif token.value == ".goto":
                    self.buffer.seek(self.get_value(tokens[i + 1])) # type: ignore
                    i += 2
                    continue
                elif token.value == ".def":
                    self.symbol_table[self.get_id(tokens[i + 1])] = self.get_bytes(tokens[i + 2])
                    i += 3
                    continue
                elif token.value == ".repeat":
                    self._write(self.get_value(tokens[i + 1]) * self.get_bytes(tokens[i + 2]), token) # type: ignore
                    i += 3
                    continue
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
            i += 1

    def get_bytes(self, token: Token) -> bytes:
        if token.type == "xint":
            return int(token.value, 16).to_bytes(4, self.byteorder )# type: ignore
        elif token.type == "dint":
            return int(token.value).to_bytes(4, self.byteorder) # type: ignore
        elif token.type == "bstr":
            return bytes(token.value, self.encoding)
        elif token.type == "zstr":
            return bytes(token.value, self.encoding) + b"\x00"
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
