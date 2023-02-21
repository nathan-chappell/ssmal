import typing as T

class SuffixMap:
    assembler_file_suffix: str = ".al"
    object_file_suffix: str = ".bin"
    debug_file_suffix: str = ".ssmdebug.json"

    def iter_suffixes(self) -> T.Generator[str, None, None]:
        yield self.assembler_file_suffix
        yield self.object_file_suffix
        yield self.debug_file_suffix

class InputFileVariant:
    suffix_map = SuffixMap()

    original_name: str
    base_name: str

    def __init__(self, s: str):
        self.original_name = s
        base_name = s
        for suffix in self.suffix_map.iter_suffixes():
            if base_name.endswith(suffix):
                base_name = base_name[: -len(suffix)]
                break
        self.base_name = base_name

    @property
    def assembler_filename(self) -> str:
        return self.base_name + self.suffix_map.assembler_file_suffix

    @property
    def object_filename(self) -> str:
        return self.base_name + self.suffix_map.object_file_suffix

    @property
    def debug_filename(self) -> str:
        return self.base_name + self.suffix_map.debug_file_suffix
