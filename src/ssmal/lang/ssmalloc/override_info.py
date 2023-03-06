from enum import Enum


class OverrideInfo(Enum):
    DoesNotOverride = 1
    DoesOverride = 2
    DeclaresNew = 3
