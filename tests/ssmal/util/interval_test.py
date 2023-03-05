from ssmal.util.interval import Interval


def test_ge():
    i1 = Interval(0, 3)
    i2 = Interval(1, 2)
    assert i1 >= i2


def test_and():
    i1 = Interval(0, 3)
    i2 = Interval(1, 2)
    assert i1 & i2 == i2
    i3 = Interval(3, 4)
    assert not (i2 & i3)


def test_or():
    i1 = Interval(1, 2)
    i2 = Interval(3, 4)
    assert (i1 | i2) == Interval(1, 4)


def test_in():
    i1 = Interval(0, 3)
    assert 1 in i1
    assert 4 not in i1
