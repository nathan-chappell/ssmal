def f(x: int) -> str: ...
def g(s: str) -> None: ...
def h(a: 'A', b: 'B') -> 'C': ...

class B: ...
class D(B): ...

x: int = 0
y: str = f(x)
z = g(y)

T = str
t: T

a: 'A'
b: 'B'
c = h(a,b)