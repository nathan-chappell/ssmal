from collections import OrderedDict

from ssmal.lang.ssmalloc.ssmal_type import SsmalType


class SsmalTypeUtil:
    
    @classmethod
    def _construct_vtable(cls, type: type, base: SsmalType | None, method_impl_map: dict[str, int]) -> tuple[tuple[int], tuple[str]]:
        type_name = type.__name__
        base_vtable_items: list[tuple[str, int]] = list(zip(base.vtable_names, base.vtable)) if base is not None else []
        base_vtable: OrderedDict[str, int] = OrderedDict(base_vtable_items)

        defined_methods: OrderedDict[str, int] = OrderedDict(
            (method_name, method_impl_map.get(f"{type_name}.{method_name}", -1))
            for method_name, method in type.__dict__.items()
            if "__" not in method_name and callable(method)
        )
        vtable = base_vtable | defined_methods
        for method_name in vtable.keys():
            assert vtable[method_name] != -1

        addresses = tuple(vtable.values())
        names = tuple(vtable.keys())
        return addresses, names
