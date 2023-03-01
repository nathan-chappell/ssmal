# INIT   1     FAIL    1  R
# check_input__first_1s  2    FAIL   2     R
# check_input__second_1s     1   FAIL  1    R



INIT     1   check_input__first_1s     1   R

check_input__first_1s   1   check_input__first_1s   1   R
check_input__first_1s   2   check_input__first_2s   2   R
check_input__first_2s   2   check_input__first_2s   2   R
check_input__first_2s   1   check_input__second_1s  1   R

check_input__second_1s  1   check_input__second_1s  1   R
check_input__second_1s  2   check_input__second_2s  2   R
check_input__second_2s  2   check_input__second_2s  2   R
check_input__second_2s  0   init_erase_1            1   L

init_erase_1    2   init_erase_1        2   L
init_erase_1    1   erase_1__from_right 1   STAY

erase_1__from_right 1   erase_1__from_left  0   L
erase_1__from_left  1   erase_1__from_left  1   L
erase_1__from_left  2   erase_1__from_left  2   L
erase_1__from_left  0   erase_1__check_left 0   R

erase_1__check_left     1   erase_1__return_right       0   R
erase_1__return_right   1   erase_1__return_right       1   R
erase_1__return_right   2   erase_1__return_right       2   R
erase_1__return_right   0   erase_1__check_1_on_right   0   L

erase_1__check_1_on_right   1   erase_1__from_right         1   STAY
erase_1__check_1_on_right   2   erase_1__check_1_on_left    2   L
erase_1__check_1_on_left    2   erase_1__check_1_on_left    2   L
erase_1__check_1_on_left    0   init_erase_2                1   R

init_erase_2    2   init_erase_2        2   R
init_erase_2    0   erase_2__from_left  0   L

erase_2__from_left      2   erase_2__from_right         0   R
erase_2__from_right     0   erase_2__from_right         0   R
erase_2__from_right     2   erase_2__return_left        0   L
erase_2__return_left    0   erase_2__return_left        0   L
erase_2__return_left    2   erase_2__from_left          2   STAY
erase_2__return_left    1   erase_2__check_2_on_right   0   R

erase_2__check_2_on_right   0   erase_2__check_2_on_right   0   R
erase_2__check_2_on_right   1   SUCCESS                     0   STAY