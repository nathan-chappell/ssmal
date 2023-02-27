def f(x: int) -> str: ...
def g(s: str) -> None: ...
def h(a: 'A', b: 'B') -> 'C': ...

class B: ...
class D(B): ...

x: int
x = 0
y: str
y = f(x)
z: None
z = g(y)

T = str
t: T

a: 'A'
b: 'B'
c = h(a,b)