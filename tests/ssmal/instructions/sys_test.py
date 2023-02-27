import pytest

from ssmal.instructions.processor_signals import SysSignal
import ssmal.instructions.sys as sys

from ssmal.components.memory import Memory
from ssmal.components.registers import Registers


def test_SYS():
    with pytest.raises(SysSignal):
        sys.SYS(Registers(), Memory())
