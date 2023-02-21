from tests import path_fix
path_fix()

import pytest

import instructions.processor_ops as op

from components.memory import Memory
from components.registers import Registers


def test_HALT():
    m = Memory()
    r = Registers()
    with pytest.raises(op.HaltSignal):
        op.HALT(r,m)