import typing as T
from dataclasses import dataclass
from pathlib import Path

from assemblers.assembler import Assembler
from assemblers.errors import UnexpectedTokenError
from assemblers.token import Token
from assemblers.tokenizer import tokenize

TFileName = str
TByteCache = T.Dict[TFileName, bytes]
TTokenCache = T.Dict[TFileName, T.List[Token]]

@dataclass
class IncludeFileSettings:
    binary: bool = False
    filename: str = ""
    once: bool = False

class FileAssembler(Assembler):
    _byte_cache: TByteCache
    _token_cache: TTokenCache
    _imported_files: T.Set[str]


    def __init__(self):
        self._byte_cache = {}
        self._token_cache = {}
        self._imported_files = set()
    
    def include(self, settings: IncludeFileSettings, token: Token):
        includedFilePath = Path(T.cast(str, token.filename)).parent / settings.filename
        key = str(includedFilePath.resolve())
        if key in self._imported_files and settings.once:
            return
        
        if settings.binary:
            if key not in self._byte_cache:
                with open(key, 'rb') as f:
                    self._byte_cache[key] = f.read()
            self._write(self._byte_cache[key], token)
        else:
            if key not in self._token_cache:
                with open(key, 'r') as f:
                    self._token_cache[key] = list(tokenize(f.read()))
            
            def _insert(l1: list, i: int, l2: list):
                return l1[:i] + l2 + l1[i:]
            
            _insert(self.tokens, self._index, self._token_cache[key])

    def handle_directive(self, t0: Token):
        if t0.value == ".include":
            settings = IncludeFileSettings()
            ti = self.eat_token

            while ti.type == 'dir':
                if ti.value == '.bin':
                    settings.binary = True
                elif ti.value == '.once':
                    settings.once = True
                ti = self.eat_token

            if ti.type != "zstr":
                raise UnexpectedTokenError(ti, 'zstr [path to included file]')
            else:
                settings.filename = ti.value
            
            self.include(settings, t0)
        else:
            return super().handle_directive(t0)
    

