from dataclasses import dataclass

import pytest

from simpledi.service_container import ServiceLifetime, ServiceContainer, ServiceContainerException


@dataclass
class Scoped1:
    ...


@dataclass
class Scoped2:
    s1: Scoped1


@dataclass
class Transient1:
    s1: Scoped1
    s2: Scoped2


@dataclass
class Transient2:
    t1: Transient1
    s2: Scoped2


@dataclass
class BadScoped1:
    t1: Transient1


@dataclass
class BadCircular:
    t1: "BadCircular"


def test_activation():
    service_container = ServiceContainer()
    service_container.register_service(Transient1, Transient1, ServiceLifetime.transient)
    service_container.register_service(Transient2, Transient2, ServiceLifetime.transient)
    service_container.register_service(Scoped1, Scoped1, ServiceLifetime.scoped)
    service_container.register_service(Scoped2, Scoped2, ServiceLifetime.scoped)

    t1 = service_container.create_service(Transient1)
    t2 = service_container.create_service(Transient2)
    s1 = service_container.create_service(Scoped1)
    s2 = service_container.create_service(Scoped2)

    assert t1 is not t2.t1
    assert s1 is s2.s1


def test_failure():
    service_container = ServiceContainer()
    service_container.register_service(Transient1, Transient1, ServiceLifetime.transient)
    service_container.register_service(BadScoped1, BadScoped1, ServiceLifetime.scoped)

    with pytest.raises(ServiceContainerException):
        service_container.create_service(BadScoped1)


def test_circular():
    service_container = ServiceContainer()
    service_container.register_service(BadCircular, BadCircular, ServiceLifetime.scoped)

    with pytest.raises(ServiceContainerException):
        service_container.create_service(BadCircular)
