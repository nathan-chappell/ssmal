from collections import OrderedDict

from ssmal.lang.ssmalloc.override_info import OverrideInfo


def _merge_tables(methods: tuple[str, ...], base_methods: tuple[str, ...]) -> OrderedDict[str, OverrideInfo]:
    result = OrderedDict[str, OverrideInfo]()
    for name in base_methods:
        if name in methods:
            result[name] = OverrideInfo.DoesOverride
        else:
            result[name] = OverrideInfo.DoesNotOverride
    for name in methods:
        if name in result:
            continue
        else:
            result[name] = OverrideInfo.DeclaresNew
    return result
