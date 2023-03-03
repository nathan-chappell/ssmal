import io
from typing import Literal

from ssmal.processors.opcodes import opcode_map
from ssmal.assemblers.errors import UnexpectedTokenError, UnresolvedLabelError
from ssmal.assemblers.label import Label
from ssmal.assemblers.token import Token

TByteOrder = Literal["little", "big"]


class Assembler:
    byteorder: TByteOrder = "little"
    encoding: Literal["ascii", "latin1"] = "ascii"

    buffer: io.BytesIO
    labels: dict[str, Label]
    source_map: dict[int, Token]
    symbol_table: dict[str, bytes]
    tokens: list[Token]

    _index: int

    def __init__(self, tokens: list[Token]):
        self.buffer = io.BytesIO()
        self.labels = {}
        self.source_map = {}
        self.symbol_table = {v.__name__.lower(): k for k, v in opcode_map.items()}
        self.tokens = tokens
        self._index = 0

    @property
    def current_position(self) -> int:
        return self.buffer.tell()

    @property
    def current_position_bytes(self) -> bytes:
        return self.current_position.to_bytes(4, self.byteorder)

    def assemble(self):
        while self._index < len(self.tokens):
            self.advance()
        self.resolve_labels()

    def eat_token(self) -> Token:
        token = self.tokens[self._index]
        self._index += 1
        return token

    def emit(self, _bytes: bytes, token: Token):
        self.buffer.write(_bytes)
        for i in range(len(_bytes)):
            self.source_map[self.current_position + i] = token

    def advance(self):
        token = self.eat_token()
        if token.type == "label":
            _id = self._get_str_value(token)
            if _id in self.labels:
                self.labels[_id].address = self.current_position
            else:
                self.labels[_id] = Label(address=self.current_position, references=[], token=token)
        if token.type == "label-ref":
            _id = self._get_str_value(token)
            if _id in self.labels:
                self.labels[_id].references.append((self.current_position, token))
            else:
                self.labels[_id] = Label(address=-1, references=[(self.current_position, token)], token=token)
        elif token.type == "id":
            self.emit(self.symbol_table[self.get_symbol(token)], token)
        elif token.type in ("xint", "dint", "bstr", "zstr"):
            self.emit(self.get_bytes(token), token)
        elif token.type == "comment":
            pass
        elif token.type == "ws":
            pass
        elif token.type == "dir":
            self.handle_directive(token)
        else:
            raise NotImplementedError()

    def resolve_labels(self):
        for label in self.labels.values():
            if label.address == -1:
                raise UnresolvedLabelError(label)
            _label_bytes = label.address.to_bytes(4, self.byteorder)
            for address, token in label.references:
                self.buffer.seek(address)
                self.emit(_label_bytes, token)

    def handle_directive(self, t0: Token):
        if t0.value == ".here":
            self.emit(self.current_position_bytes, t0)
        else:
            t1 = self.eat_token()
            if t0.value == ".byteorder":
                self.byteorder = self.get_byteorder(t1)
            elif t0.value == ".encoding":
                self.encoding = self.get_encoding(t1)
            elif t0.value == ".goto":
                self.buffer.seek(self.get_address(t1))
            else:
                t2 = self.eat_token()
                if t0.value == ".def":
                    self.symbol_table[self.get_symbol(t1)] = self.get_bytes(t2)
                # elif t0.value == ".repeat":
                #     self.emit(cast(int, self.get_repeated_value(t1)) * self.get_bytes(t2), t0)
                else:
                    raise UnexpectedTokenError(t0, "Error processing directive.")

    def _get_int_value(self, token: Token) -> int:
        if token.type == "xint":
            return int(token.value, 16)
        elif token.type == "dint":
            return int(token.value)
        elif token.type == "id":
            return int.from_bytes(self.symbol_table[token.value], byteorder=self.byteorder, signed=True)
        else:
            raise UnexpectedTokenError(token, "xint, dint, id")

    def _get_str_value(self, token: Token) -> str:
        if token.type in ("bstr", "zstr"):
            return token.value[1:-1]
        else:
            raise UnexpectedTokenError(token, "bstr, zstr")

    def get_address(self, token: Token) -> int:
        return self._get_int_value(token)

    def get_byteorder(self, token: Token) -> TByteOrder:
        result = self._get_str_value(token)
        if result in ("little", "big"):
            return result
        else:
            raise UnexpectedTokenError(token, '"little", "big"')

    def get_bytes(self, token: Token) -> bytes:
        if token.type == "xint":
            return int(token.value, 16).to_bytes(4, self.byteorder)
        elif token.type == "dint":
            return int(token.value).to_bytes(4, self.byteorder)
        elif token.type == "bstr":
            return bytes.fromhex(token.value[1:-1])
        elif token.type == "zstr":
            return bytes(token.value[1:-1], self.encoding) + b"\x00"
        else:
            raise UnexpectedTokenError(token, "xint, dint, bstr, zstr")

    def get_encoding(self, token: Token) -> Literal["ascii", "latin1"]:
        result = self._get_str_value(token)
        if result in ("ascii", "latin1"):
            return result
        else:
            raise UnexpectedTokenError(token, '"ascii", "latin1"')

    # def get_repeated_value(self, token: Token) -> int | str | bytes
    #     if token.type == "xint":
    #         return int(token.value, 16)
    #     elif token.type == "dint":
    #         return int(token.value)
    #     elif token.type == "bstr":
    #         return bytes(token.value[1:-1], self.encoding)
    #     elif token.type == "zstr":
    #         return token.value[1:-1]
    #     elif token.type == "id":
    #         return self.symbol_table[token.value]
    #     else:
    #         raise UnexpectedTokenError(token, "xint, dint, bstr, zstr, id")

    def get_symbol(self, token: Token) -> str:
        if token.type == "id":
            return token.value
        else:
            raise UnexpectedTokenError(token, "id")
