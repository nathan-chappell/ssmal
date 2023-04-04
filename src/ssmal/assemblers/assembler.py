from dataclasses import asdict
import io
import json
from typing import Literal

from ssmal.processors.opcodes import opcode_map
from ssmal.assemblers.errors import UnexpectedTokenError, UnresolvedLabelError
from ssmal.assemblers.resolvable import Resolvable
from ssmal.assemblers.token import Token
from ssmal.util.hexdump_bytes import hexdump_bytes

TByteOrder = Literal["little", "big"]


class Assembler:
    byteorder: TByteOrder = "little"
    encoding: Literal["ascii", "latin1"] = "ascii"
    alignment = 0x20

    buffer: io.BytesIO
    labels: dict[str, Resolvable]
    source_map: dict[int, Token]
    symbol_table: dict[str, bytes]
    tokens: list[Token]
    # unresolved_symbols: dict[str, Resolvable] # this was not a good idea.

    DEBUG_INFO_VERSION = "0.0"
    _index: int

    UNRESOLVED_ADDRESS_MARKER = -1

    # UNRESOLVED_ADDRESS_BYTES = (-1).to_bytes(4, 'little')
    @property
    def unresolved_address_bytes(self) -> bytes:
        return self.UNRESOLVED_ADDRESS_MARKER.to_bytes(4, self.byteorder, signed=True)

    @property
    def debug_info(self) -> str:
        _debug_info = {f'0x{offset:04x}': asdict(token) for offset, token in self.source_map.items()}
        _labels = {label.token.value: f"{label.address:08x}" for label in self.labels.values() if label.token is not None}
        return json.dumps({"version": self.DEBUG_INFO_VERSION, "labels": _labels, "source_map": _debug_info}, indent=2)

    def __init__(self, tokens: list[Token]):
        self.buffer = io.BytesIO()
        self.labels = {}
        self.source_map = {}
        self.symbol_table = {v.__name__.lower(): k for k, v in opcode_map.items()}
        self.tokens = tokens
        # self.unresolved_symbols = {}
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
        self._resolve_labels()
        # self._resolve_symbols()

    def eat_token(self) -> Token:
        token = self.tokens[self._index]
        self._index += 1
        return token

    def emit(self, _bytes: bytes, token: Token):
        for i in range(len(_bytes)):
            self.source_map[self.current_position + i] = token
        self.buffer.write(_bytes)

    def _update_resolvable(self, name: str, which_dict: Literal["labels"], action: Literal["ref", "def"], token: Token):
        _dict: dict[str, Resolvable] = getattr(self, which_dict)
        if action == "ref":
            if name in _dict:
                _dict[name].references.append((self.current_position, token))
            else:
                _dict[name] = Resolvable(address=self.UNRESOLVED_ADDRESS_MARKER, references=[(self.current_position, token)])
        if action == "def":
            if name in _dict and _dict[name].address != self.UNRESOLVED_ADDRESS_MARKER:
                raise UnexpectedTokenError(token, "Label redefinition.")
            elif name in _dict:
                _dict[name].address = self.current_position
                _dict[name].token = token
            else:
                _dict[name] = Resolvable(address=self.current_position, references=[], token=token)

    def advance(self):
        token = self.eat_token()
        if token.type == "label":
            label_name = token.value[:-1]
            self._update_resolvable(label_name, "labels", "def", token)
        elif token.type == "label-ref":
            label_name = token.value[1:]
            self._update_resolvable(label_name, "labels", "ref", token)
            self.emit(self.unresolved_address_bytes, token)
        elif token.type == "id":
            _symbol = self.get_symbol(token)
            if _symbol in self.symbol_table:
                self.emit(self.symbol_table[_symbol], token)
            else:
                raise UnexpectedTokenError(token, f"Undefined symbol: {token.value}")
                # self._update_resolvable(token.value, "unresolved_symbols", "ref", token)
                # self.emit(self.UNRESOLVED_ADDRESS_BYTES, token)
        elif token.type in ("xint", "dint", "bstr", "zstr"):
            self.emit(self.get_bytes(token), token)
        elif token.type == "comment":
            pass
        elif token.type == "ws":
            pass
        elif token.type == "dir":
            self.handle_directive(token)
        else:
            raise UnexpectedTokenError(token, "Unknown token")

    def _resolve_labels(self):
        for label in self.labels.values():
            if label.address == -1:
                raise UnresolvedLabelError(label)
            _label_bytes = label.address.to_bytes(4, self.byteorder)
            for address, token in label.references:
                self.buffer.seek(address)
                _cur_val = int.from_bytes(self.buffer.read(4), self.byteorder, signed=True)
                if _cur_val != self.UNRESOLVED_ADDRESS_MARKER:
                    raise Exception("Double-resolution", label)
                self.buffer.seek(address)
                self.emit(_label_bytes, token)

    # def _resolve_symbols(self):
    #     for symbol in self.unresolved_symbols.values():
    #         if symbol.token is None:
    #             raise UnresolvedLabelError(symbol)
    #         _symbol_bytes = self.symbol_table[symbol.token.value]
    #         for address, token in symbol.references:
    #             self.buffer.seek(address)
    #             self.emit(_symbol_bytes, token)

    def handle_directive(self, t0: Token):
        if t0.value == ".here":
            self.emit(self.current_position_bytes, t0)
        elif t0.value == ".align":
            _bytes_to_alignment = b"\x00" * (self.alignment - self.current_position % self.alignment)
            self.emit(_bytes_to_alignment, t0)
        else:
            t1 = self.eat_token()
            if t0.value == ".byteorder":
                self.byteorder = self.get_byteorder(t1)
            elif t0.value == ".encoding":
                self.encoding = self.get_encoding(t1)
            elif t0.value == ".goto":
                self.buffer.seek(self.get_address(t1))
            elif t0.value == ".zeros":
                self.emit(b"\x00" * self._get_int_value(t1), t0)
            else:
                t2 = self.eat_token()
                if t0.value == ".def":
                    _symbol = self.get_symbol(t1)
                    if _symbol in self.symbol_table:
                        raise UnexpectedTokenError(t1, "Symbol redefinition.")
                    self.symbol_table[_symbol] = self.get_bytes(t2)
                    # if _symbol in self.unresolved_symbols:
                    #     self.unresolved_symbols[_symbol].token = t1

                    # self.emit(cast(int, self.get_repeated_value(t1)) * self.get_bytes(t2), t0)
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
            return int(token.value).to_bytes(4, self.byteorder, signed=True)
        elif token.type == "bstr":
            return bytes.fromhex(token.value[1:-1])
        elif token.type == "zstr":
            return bytes(token.value[1:-1], self.encoding) + b"\x00"
        elif token.type == "dir" and token.value == ".here":
            return self.buffer.tell().to_bytes(4, self.byteorder, signed=True)
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
