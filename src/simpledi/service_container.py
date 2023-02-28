from dataclasses import dataclass
from enum import Enum
from inspect import signature, Parameter
from typing import TypeVar, Any


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
        service_info = self.service_info[service]

        if service_info.lifetime == ServiceLifetime.scoped and service in self.active_services:
            return self.active_services[service]

        implementation = self.get_implementation(service)
        constructor = implementation.__init__
        constructor_signature = signature(constructor)
        dependencies: dict[str, Any] = {}
        for parameter_name, parameter in list(constructor_signature.parameters.items()):
            if parameter_name == "self":
                continue
            # dependency = self.get_parameter(parameter)
            dependent_service_info = self.get_parameter_info(parameter)
            if dependent_service_info.lifetime.value < service_info.lifetime.value:
                raise ServiceContainerException(f"Invalid dependency: {service_info=} depends on {dependent_service_info=}")
            if dependent_service_info.lifetime == ServiceLifetime.scoped and dependent_service_info.service in self.active_services:
                dependencies[parameter_name] = self.active_services[dependent_service_info.service]
            else:
                dependencies[parameter_name] = self.create_service(dependent_service_info.service)
        bound_parameters = constructor_signature.bind_partial(**dependencies)
        result = implementation(*bound_parameters.args, **bound_parameters.kwargs)

        if service_info.lifetime == ServiceLifetime.scoped:
            self.active_services[service] = result

        self.active_services[service] = result
        return result

    def get_parameter_info(self, parameter: Parameter) -> ServiceInfo:
        if parameter.kind != Parameter.POSITIONAL_OR_KEYWORD:
            raise ServiceContainerException(f"only POSITIONAL_OR_KEYWORD parameters in service constructors", parameter)
        elif parameter.annotation == Parameter.empty:
            raise ServiceContainerException(f"all service parameters require annotations", parameter)
        elif isinstance(parameter.annotation, str):
            raise ServiceContainerException(f"all service parameters require NON-STRING annotations", parameter)
        else:
            return self.service_info[parameter.annotation]
