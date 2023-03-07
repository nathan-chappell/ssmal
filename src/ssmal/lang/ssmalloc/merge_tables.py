from collections import OrderedDict

from ssmal.lang.ssmalloc.override_type import OverrideType


def merge_tables(methods: tuple[str, ...], base_methods: tuple[str, ...]) -> OrderedDict[str, OverrideType]:
    result = OrderedDict[str, OverrideType]()
    for name in base_methods:
        if name in methods:
            result[name] = OverrideType.DoesOverride
        else:
            result[name] = OverrideType.DoesNotOverride
    for name in methods:
        if name in result:
            continue
        else:
            result[name] = OverrideType.DeclaresNew
    return result
