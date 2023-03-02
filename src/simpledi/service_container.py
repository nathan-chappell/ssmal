from dataclasses import dataclass
from enum import Enum
from inspect import signature, Parameter
from typing import TypeVar, Any, get_type_hints


TService = TypeVar("TService")
TServiceImpl = TypeVar("TServiceImpl")


class ServiceContainerException(Exception):
    ...


class ServiceLifetime(Enum):
    transient = 1
    scoped = 2


@dataclass
class ServiceInfo:
    service: type
    implementation: type
    lifetime: ServiceLifetime = ServiceLifetime.transient


class ServiceContainer:
    active_services: dict[type, Any]
    service_info: dict[type, ServiceInfo]

    def __init__(self) -> None:
        self.active_services = {}
        self.service_info = {}

    def get_implementation(self, service: type) -> type:
        if service not in self.service_info:
            raise ServiceContainerException(service, service)
        return self.service_info[service].implementation

    def register_service(self, service: type, service_impl: type, lifetime: ServiceLifetime = ServiceLifetime.scoped):
        if not issubclass(service_impl, service):
            raise ServiceContainerException(service, service_impl)
        self.service_info[service] = ServiceInfo(service, service_impl, lifetime)

    def create_service(self, service: type[TService]) -> TService:
        return self._create_service(service, [])

    def _create_service(self, service: type[TService], service_creation_stack: list[type]) -> TService:
        service_info = self.service_info[service]

        if service_info.lifetime == ServiceLifetime.scoped and service in self.active_services:
            return self.active_services[service]

        implementation = self.get_implementation(service)
        constructor = implementation.__init__
        constructor_signature = signature(constructor)
        constructor_type_hints = get_type_hints(constructor)
        dependencies: dict[str, Any] = {}

        for parameter_name in constructor_signature.parameters.keys():
            if parameter_name == "self":
                continue

            dependent_service_type_hint = constructor_type_hints.get(parameter_name, None)
            if not isinstance(dependent_service_type_hint, type):
                raise ServiceContainerException(f"Invalid constructor: {signature=} has non-type annotation")
            if dependent_service_type_hint not in self.service_info:
                raise ServiceContainerException(f"Invalid constructor: {dependent_service_type_hint=} is not registered")

            dependent_service_info = self.service_info[dependent_service_type_hint]

            if dependent_service_info.lifetime.value < service_info.lifetime.value:
                raise ServiceContainerException(f"Invalid dependency: {service_info=} depends on {dependent_service_info=}")
            if dependent_service_info.lifetime == ServiceLifetime.scoped and dependent_service_info.service in self.active_services:
                dependencies[parameter_name] = self.active_services[dependent_service_info.service]
            elif dependent_service_info.service in service_creation_stack:
                raise ServiceContainerException(f"Circular dependency: {dependent_service_info=} {service_creation_stack=}")
            else:
                dependencies[parameter_name] = self._create_service(dependent_service_info.service, [service, *service_creation_stack])
        bound_parameters = constructor_signature.bind_partial(**dependencies)
        result = implementation(*bound_parameters.args, **bound_parameters.kwargs)

        if service_info.lifetime == ServiceLifetime.scoped:
            self.active_services[service] = result

        self.active_services[service] = result
        return result
