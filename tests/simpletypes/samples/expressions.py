x: int
y: str
x = 0
y = 'foobar'
def f(x: int, y: str) -> str: ...
y = f(x, f(123, y))