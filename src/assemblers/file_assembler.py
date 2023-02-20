import typing as T
from dataclasses import dataclass, replace
from pathlib import Path

from assemblers.assembler import Assembler
from assemblers.errors import UnexpectedTokenError
from assemblers.token import Token
from assemblers.tokenizer import tokenize

TFileName = str
TByteCache = T.Dict[TFileName, bytes]
TTokenCache = T.Dict[TFileName, T.List[Token]]

def _insert(l1: list, i: int, l2: list):
                return l1[:i] + l2 + l1[i:]

@dataclass
class IncludeFileSettings:
    binary: bool = False
    filename: str = ""
    once: bool = False


class FileAssembler(Assembler):
    _byte_cache: TByteCache
    _token_cache: TTokenCache

    def __init__(self):
        super().__init__([])
        self._byte_cache = {}
        self._token_cache = {}
    
    def assemble_file(self, filename: str):
        self._insert_tokens(list(self._tokenize(filename)))
        self.assemble()
    
    def _tokenize(self, filename: str) -> T.Generator[Token, None, None]:
        with open(filename, 'r') as f:
            text = f.read()
        for token in tokenize(text):
            yield replace(token, filename=filename)
    
    def _insert_tokens(self, tokens: T.List[Token]):
        self.tokens = _insert(self.tokens, self._index, tokens)
    
    def _already_include(self, filename: str) -> bool:
        return filename in self._byte_cache or filename in self._token_cache

    def _include(self, settings: IncludeFileSettings, token: Token):
        included_file_path = Path(T.cast(str, token.filename)).parent / settings.filename
        included_file_fullname = str(included_file_path.resolve())
        if self._already_include(included_file_fullname) and settings.once:
            return

        if settings.binary:
            if included_file_fullname not in self._byte_cache:
                with open(included_file_fullname, "rb") as f:
                    self._byte_cache[included_file_fullname] = f.read()
            self.emit(self._byte_cache[included_file_fullname], token)
        else:
            if included_file_fullname not in self._token_cache:
                self._token_cache[included_file_fullname] = list(self._tokenize(included_file_fullname))
            self._insert_tokens(self._token_cache[included_file_fullname])

    def handle_directive(self, t0: Token):
        if t0.value == ".include":
            settings = IncludeFileSettings()
            ti = self.eat_token()

            while ti.type == "dir":
                if ti.value == ".binary":
                    settings.binary = True
                elif ti.value == ".once":
                    settings.once = True
                else:
                    raise UnexpectedTokenError(ti, "dir.binary | dir.once")
                ti = self.eat_token()

            if ti.type != "zstr":
                raise UnexpectedTokenError(ti, "zstr [path to included file]")
            else:
                settings.filename = self._get_str_value(ti)

            self._include(settings, t0)
        else:
            return super().handle_directive(t0)
