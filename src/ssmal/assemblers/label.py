from dataclasses import dataclass

from ssmal.assemblers.token import Token

@dataclass
class Label:
    address: int
    references: list[tuple[int, Token]]
    token: Token
