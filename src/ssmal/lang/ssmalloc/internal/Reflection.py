from __future__ import annotations
from ssmal.lang.ssmalloc.internal.System import *
from ssmal.lang.ssmalloc.stdlib import *


@dataclass
class Reflection:
    @classmethod
    def get_field(cls, obj: Ptr, name: String) -> Any:
        ...

    @classmethod
    def call_method(cls, obj: Ptr, name: String, *args) -> Any:
        ...
