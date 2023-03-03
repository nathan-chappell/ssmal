class InputFileVariant:
    assembler_file_suffix: str = ".al"
    object_file_suffix: str = ".bin"
    debug_file_suffix: str = ".ssmdebug.json"
    tm_file_suffix: str = ".tm"

    original_name: str
    base_name: str

    def __init__(self, s: str):
        self.original_name = s
        base_name = s
        for suffix in (self.assembler_file_suffix, self.object_file_suffix, self.debug_file_suffix, self.tm_file_suffix):
            if base_name.endswith(suffix):
                base_name = base_name[: -len(suffix)]
                break
        self.base_name = base_name

    @property
    def assembler_filename(self) -> str:
        return self.base_name + self.assembler_file_suffix
    
    @property
    def is_assembler_file(self) -> bool:
        return self.original_name.endswith(self.assembler_file_suffix)

    @property
    def object_filename(self) -> str:
        return self.base_name + self.object_file_suffix
    
    @property
    def is_object_file(self) -> bool:
        return self.original_name.endswith(self.object_file_suffix)

    @property
    def debug_filename(self) -> str:
        return self.base_name + self.debug_file_suffix
    
    @property
    def is_debug_file(self) -> bool:
        return self.original_name.endswith(self.debug_file_suffix)

    @property
    def tm_filename(self) -> str:
        return self.base_name + self.tm_file_suffix
    
    @property
    def is_tm_file(self) -> bool:
        return self.original_name.endswith(self.tm_file_suffix)
