
from typing import Any
from ssmal.lang.ssmalloc.metadata.arena import Arena
from ssmal.processors.processor import Processor

"""
embeddable_type: should be built-in types:
    * int
    * str
    * bytearray
    * T where T is a dataclass with fields whose types are embeddable_types
    * tuple[T, n] # finite tuple
    * tuple[T, ...] # built-in array
"""

class RtProxy:
    address: int
    arena: Arena
    processor: Processor
    proxied_type: type

    def __init__(self, arena: Arena, embeddable_type: type) -> None:
        # TODO:
        # need a builtin_types module
        # - operations for embeddable_types...
        # - calculating size...
        self.address = -1
        self.arena = arena
        self.processor = Processor()
        self.proxied_type = embeddable_type

    def __getattribute__(self, name) -> Any:
        """Get the attribute from the arena using a processor"""
        ...
    
    def __setattr__(self, name) -> Any:
        """Set the attribute from the arena using a processor"""
        ...


class RtEmbeddable:
    arena: Arena

    def __init__(self, arena: Arena) -> None:
        self.arena = arena

    def embed(self) -> None:
        raise NotImplementedError()
    
    @classmethod
    def hydrate(cls, address) -> RtProxy:
        ...