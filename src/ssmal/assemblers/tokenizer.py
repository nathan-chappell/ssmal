import re
import typing as T

from ssmal.assemblers.token import Token

_tokens: list[T.Tuple[str, str]] = [
    ("id", r"[a-zA-Z_][a-zA-Z_0-9.]*"),
    ("dir", r"\.[a-zA-Z][a-zA-Z_0-9]*"),
    ("xint", r"0x[0-9]+"),
    ("dint", r"[0-9]+"),
    ("bstr", r"'(''|[^'])*'"),
    ("zstr", r'"(\\\\|\\"|[^"])*"'),
    ("comment", r";[^\n]*"),
    ("ws", r"\s+"),
]


def tokenize(input: str) -> T.Generator[Token, None, None]:
    position = 0
    line = 0
    column = 0

    matchers = [(name, re.compile(pattern)) for name, pattern in _tokens]

    while position < len(input):
        for name, regex in matchers:
            match = regex.match(input, pos=position)
            if match:
                position += len(match[0])
                # filter ws
                if name != "ws":
                    yield Token(type=name, value=match[0], line=line, column=column)
                # deal with line/column
                if "\n" in match[0]:
                    line += match[0].count("\n")
                    column = len(match[0]) - (match[0].rindex("\n") + 1)
                else:
                    column += len(match[0])
                # break to while loop
                break
