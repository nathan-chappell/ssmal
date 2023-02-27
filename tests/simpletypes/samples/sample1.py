class B: ...
class D(B): ...

def f(x: int) -> str: ...
def g(s: str) -> None: ...
def h(a: D, b: B) -> int: ...

x: int
x = 0
y: str
y = f(x)
z: None
z = g(y)

T: type = str
t: T

a: D
b: B
c = h(a,b)