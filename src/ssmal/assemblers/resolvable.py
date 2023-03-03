from dataclasses import dataclass

from ssmal.assemblers.token import Token

@dataclass
class Resolvable:
    address: int
    references: list[tuple[int, Token]]
    token: Token | None = None
