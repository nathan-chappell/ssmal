import re

from typing import Generator

from ssmal.lang.tm.transtion import TmTransition


class TmParseError(Exception):
    ...


def _get_lines(text: str) -> Generator[str, None, None]:
    for line in text.split("\n"):
        line = line.strip()
        if not line:
            continue
        if line[0] == "#":
            continue
        yield line


def parse_tm_transitions(text: str) -> Generator[TmTransition, None, None]:
    line_regex = re.compile(
        r"""
        (?P<cur_state>\w+)   #
        \s+
        (?P<cur_symbol>\w+)  # cur_symbol
        \s+
        (?P<next_state>\w+)  # next_state
        \s+
        (?P<next_symbol>\w+) # next_symbol
        \s+
        (?P<move_head>\w+)   # move_head
    """,
        re.VERBOSE,
    )
    for line in _get_lines(text):
        line_match = line_regex.match(line)
        match line_match.groupdict() if line_match else None:
            case {
                "cur_state": str(cur_state),
                "cur_symbol": ("0" | "1" | "2") as cur_symbol,
                "next_state": str(next_state),
                "next_symbol": ("0" | "1" | "2") as next_symbol,
                "move_head": ("L" | "R" | "STAY") as move_head,
            }:
                yield TmTransition(cur_state, cur_symbol, next_state, next_symbol, move_head)
            case _:  # pragma: no cover
                raise TmParseError(f"failed to parse {line=}")


if __name__ == "__main__":  # pragma: no cover
    import argparse
    import pprint
    import sys

    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("filename")

    args = arg_parser.parse_args(sys.argv[1:])

    with open(args.filename) as f:
        pprint.pprint(list(parse_tm_transitions(f.read())))
