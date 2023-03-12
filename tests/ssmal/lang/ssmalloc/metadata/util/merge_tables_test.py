import pytest

from ssmal.lang.ssmalloc.metadata.util.merge_tables import merge_tables
from ssmal.lang.ssmalloc.metadata.util.override_type import OverrideType


def test_merge_tables():
    methods = ['f','g']
    base_methods = ['f','h']
    assert merge_tables(methods, base_methods) == {
        'f': OverrideType.DoesOverride,
        'g': OverrideType.DeclaresNew,
        'h': OverrideType.DoesNotOverride,
    }