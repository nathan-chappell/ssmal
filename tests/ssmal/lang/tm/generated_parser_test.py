import pytest

from ssmal.lang.tm.parser import parse_tm_transitions, TmTransition, TmParseError

# tests/ssmal/lang/tm/samples/double_counter.tm

double_counter_expected = [
    TmTransition(cur_state="INIT", cur_symbol="1", next_state="check_input__first_1s", next_symbol="1", move_head="R"),
    TmTransition(cur_state="check_input__first_1s", cur_symbol="1", next_state="check_input__first_1s", next_symbol="1", move_head="R"),
    TmTransition(cur_state="check_input__first_1s", cur_symbol="2", next_state="check_input__first_2s", next_symbol="2", move_head="R"),
    TmTransition(cur_state="check_input__first_2s", cur_symbol="2", next_state="check_input__first_2s", next_symbol="2", move_head="R"),
    TmTransition(
        cur_state="check_input__first_2s", cur_symbol="1", next_state="check_input__second_1s", next_symbol="1", move_head="R"
    ),
    TmTransition(
        cur_state="check_input__second_1s", cur_symbol="1", next_state="check_input__second_1s", next_symbol="1", move_head="R"
    ),
    TmTransition(
        cur_state="check_input__second_1s", cur_symbol="2", next_state="check_input__second_2s", next_symbol="2", move_head="R"
    ),
    TmTransition(
        cur_state="check_input__second_2s", cur_symbol="2", next_state="check_input__second_2s", next_symbol="2", move_head="R"
    ),
    TmTransition(cur_state="check_input__second_2s", cur_symbol="0", next_state="init_erase_1", next_symbol="1", move_head="L"),
    TmTransition(cur_state="init_erase_1", cur_symbol="2", next_state="init_erase_1", next_symbol="2", move_head="L"),
    TmTransition(cur_state="init_erase_1", cur_symbol="1", next_state="erase_1__from_right", next_symbol="1", move_head="STAY"),
    TmTransition(cur_state="erase_1__from_right", cur_symbol="1", next_state="erase_1__from_left", next_symbol="0", move_head="L"),
    TmTransition(cur_state="erase_1__from_left", cur_symbol="1", next_state="erase_1__from_left", next_symbol="1", move_head="L"),
    TmTransition(cur_state="erase_1__from_left", cur_symbol="2", next_state="erase_1__from_left", next_symbol="2", move_head="L"),
    TmTransition(cur_state="erase_1__from_left", cur_symbol="0", next_state="erase_1__check_left", next_symbol="0", move_head="R"),
    TmTransition(cur_state="erase_1__check_left", cur_symbol="1", next_state="erase_1__return_right", next_symbol="0", move_head="R"),
    TmTransition(cur_state="erase_1__return_right", cur_symbol="1", next_state="erase_1__return_right", next_symbol="1", move_head="R"),
    TmTransition(cur_state="erase_1__return_right", cur_symbol="2", next_state="erase_1__return_right", next_symbol="2", move_head="R"),
    TmTransition(
        cur_state="erase_1__return_right", cur_symbol="0", next_state="erase_1__check_1_on_right", next_symbol="0", move_head="L"
    ),
    TmTransition(
        cur_state="erase_1__check_1_on_right", cur_symbol="1", next_state="erase_1__from_right", next_symbol="1", move_head="STAY"
    ),
    TmTransition(
        cur_state="erase_1__check_1_on_right", cur_symbol="2", next_state="erase_1__check_1_on_left", next_symbol="2", move_head="L"
    ),
    TmTransition(
        cur_state="erase_1__check_1_on_left", cur_symbol="2", next_state="erase_1__check_1_on_left", next_symbol="2", move_head="L"
    ),
    TmTransition(cur_state="erase_1__check_1_on_left", cur_symbol="0", next_state="init_erase_2", next_symbol="1", move_head="R"),
    TmTransition(cur_state="init_erase_2", cur_symbol="2", next_state="init_erase_2", next_symbol="2", move_head="R"),
    TmTransition(cur_state="init_erase_2", cur_symbol="0", next_state="erase_2__from_left", next_symbol="0", move_head="L"),
    TmTransition(cur_state="erase_2__from_left", cur_symbol="2", next_state="erase_2__from_right", next_symbol="0", move_head="R"),
    TmTransition(cur_state="erase_2__from_right", cur_symbol="0", next_state="erase_2__from_right", next_symbol="0", move_head="R"),
    TmTransition(cur_state="erase_2__from_right", cur_symbol="2", next_state="erase_2__return_left", next_symbol="0", move_head="L"),
    TmTransition(cur_state="erase_2__return_left", cur_symbol="0", next_state="erase_2__return_left", next_symbol="0", move_head="L"),
    TmTransition(cur_state="erase_2__return_left", cur_symbol="2", next_state="erase_2__from_left", next_symbol="2", move_head="STAY"),
    TmTransition(
        cur_state="erase_2__return_left", cur_symbol="1", next_state="erase_2__check_2_on_right", next_symbol="0", move_head="R"
    ),
    TmTransition(
        cur_state="erase_2__check_2_on_right", cur_symbol="0", next_state="erase_2__check_2_on_right", next_symbol="0", move_head="R"
    ),
    TmTransition(cur_state="erase_2__check_2_on_right", cur_symbol="1", next_state="SUCCESS", next_symbol="0", move_head="STAY"),
]
# tests/ssmal/lang/tm/samples/ones_then_twos.tm

ones_then_twos_expected = [
    TmTransition(cur_state="reading_ones", cur_symbol="1", next_state="reading_ones", next_symbol="0", move_head="R"),
    TmTransition(cur_state="reading_ones", cur_symbol="2", next_state="reading_twos", next_symbol="0", move_head="R"),
    TmTransition(cur_state="reading_twos", cur_symbol="2", next_state="reading_twos", next_symbol="0", move_head="R"),
    TmTransition(cur_state="reading_ones", cur_symbol="0", next_state="FAIL", next_symbol="0", move_head="R"),
    TmTransition(cur_state="reading_twos", cur_symbol="0", next_state="SUCCESS", next_symbol="0", move_head="R"),
    TmTransition(cur_state="reading_twos", cur_symbol="1", next_state="FAIL", next_symbol="0", move_head="R"),
]


@pytest.mark.parametrize(
    "filename,expected",
    [
        ("tests/ssmal/lang/tm/samples/double_counter.tm", double_counter_expected),
        ("tests/ssmal/lang/tm/samples/ones_then_twos.tm", ones_then_twos_expected),
    ],
)
def test_simple_ast_parser(filename: str, expected: list[TmTransition]):
    with open(filename) as f:
        text = f.read()
    binary_transitions = list(parse_tm_transitions(text))
    assert binary_transitions == expected
