from enum import Enum


class OverrideType(Enum):
    DoesNotOverride = 1
    DoesOverride = 2
    DeclaresNew = 3
