INIT :
        swpab psha swpab;  save B to stack
        ldab addi -1;  B points to head
            brni $INIT_case_0;  head is 0
            brzi $INIT_case_1;  head is 1
            brzi $INIT_case_2;  head is 2
    .alignINIT_case_1:
        popa swpab;  restore B from stack
        ldai {value} stab;  write 1 to head
        swpab addi 1 swpab;  move R
         bri $check_input__first_1s;  goto check_input__first_1s
        .align
    .align
    check_input__first_1s :
            swpab psha swpab;  save B to stack
            ldab addi -1;  B points to head
                brni $check_input__first_1s_case_0;  head is 0
                brzi $check_input__first_1s_case_1;  head is 1
                brzi $check_input__first_1s_case_2;  head is 2
        .aligncheck_input__first_1s_case_1:
            popa swpab;  restore B from stack
            ldai {value} stab;  write 1 to head
            swpab addi 1 swpab;  move R
             bri $check_input__first_1s;  goto check_input__first_1s
            .align
        check_input__first_1s_case_2:
            popa swpab;  restore B from stack
            ldai {value} stab;  write 2 to head
            swpab addi 1 swpab;  move R
             bri $check_input__first_2s;  goto check_input__first_2s
            .align
        .align
        check_input__first_2s :
                swpab psha swpab;  save B to stack
                ldab addi -1;  B points to head
                    brni $check_input__first_2s_case_0;  head is 0
                    brzi $check_input__first_2s_case_1;  head is 1
                    brzi $check_input__first_2s_case_2;  head is 2
            .aligncheck_input__first_2s_case_2:
                popa swpab;  restore B from stack
                ldai {value} stab;  write 2 to head
                swpab addi 1 swpab;  move R
                 bri $check_input__first_2s;  goto check_input__first_2s
                .align
            check_input__first_2s_case_1:
                popa swpab;  restore B from stack
                ldai {value} stab;  write 1 to head
                swpab addi 1 swpab;  move R
                 bri $check_input__second_1s;  goto check_input__second_1s
                .align
            .align
            check_input__second_1s :
                    swpab psha swpab;  save B to stack
                    ldab addi -1;  B points to head
                        brni $check_input__second_1s_case_0;  head is 0
                        brzi $check_input__second_1s_case_1;  head is 1
                        brzi $check_input__second_1s_case_2;  head is 2
                .aligncheck_input__second_1s_case_1:
                    popa swpab;  restore B from stack
                    ldai {value} stab;  write 1 to head
                    swpab addi 1 swpab;  move R
                     bri $check_input__second_1s;  goto check_input__second_1s
                    .align
                check_input__second_1s_case_2:
                    popa swpab;  restore B from stack
                    ldai {value} stab;  write 2 to head
                    swpab addi 1 swpab;  move R
                     bri $check_input__second_2s;  goto check_input__second_2s
                    .align
                .align
                check_input__second_2s :
                        swpab psha swpab;  save B to stack
                        ldab addi -1;  B points to head
                            brni $check_input__second_2s_case_0;  head is 0
                            brzi $check_input__second_2s_case_1;  head is 1
                            brzi $check_input__second_2s_case_2;  head is 2
                    .aligncheck_input__second_2s_case_2:
                        popa swpab;  restore B from stack
                        ldai {value} stab;  write 2 to head
                        swpab addi 1 swpab;  move R
                         bri $check_input__second_2s;  goto check_input__second_2s
                        .align
                    check_input__second_2s_case_0:
                        popa swpab;  restore B from stack
                        ldai {value} stab;  write 1 to head
                        swpab addi -1 swpab;  move L
                         bri $init_erase_1;  goto init_erase_1
                        .align
                    .align
                    init_erase_1 :
                            swpab psha swpab;  save B to stack
                            ldab addi -1;  B points to head
                                brni $init_erase_1_case_0;  head is 0
                                brzi $init_erase_1_case_1;  head is 1
                                brzi $init_erase_1_case_2;  head is 2
                        .aligninit_erase_1_case_2:
                            popa swpab;  restore B from stack
                            ldai {value} stab;  write 2 to head
                            swpab addi -1 swpab;  move L
                             bri $init_erase_1;  goto init_erase_1
                            .align
                        init_erase_1_case_1:
                            popa swpab;  restore B from stack
                            ldai {value} stab;  write 1 to head
                            swpab addi 0 swpab;  move STAY
                             bri $erase_1__from_right;  goto erase_1__from_right
                            .align
                        .align
                        erase_1__from_right :
                                swpab psha swpab;  save B to stack
                                ldab addi -1;  B points to head
                                    brni $erase_1__from_right_case_0;  head is 0
                                    brzi $erase_1__from_right_case_1;  head is 1
                                    brzi $erase_1__from_right_case_2;  head is 2
                            .alignerase_1__from_right_case_1:
                                popa swpab;  restore B from stack
                                ldai {value} stab;  write 0 to head
                                swpab addi -1 swpab;  move L
                                 bri $erase_1__from_left;  goto erase_1__from_left
                                .align
                            .align
                            erase_1__from_left :
                                    swpab psha swpab;  save B to stack
                                    ldab addi -1;  B points to head
                                        brni $erase_1__from_left_case_0;  head is 0
                                        brzi $erase_1__from_left_case_1;  head is 1
                                        brzi $erase_1__from_left_case_2;  head is 2
                                .alignerase_1__from_left_case_1:
                                    popa swpab;  restore B from stack
                                    ldai {value} stab;  write 1 to head
                                    swpab addi -1 swpab;  move L
                                     bri $erase_1__from_left;  goto erase_1__from_left
                                    .align
                                erase_1__from_left_case_2:
                                    popa swpab;  restore B from stack
                                    ldai {value} stab;  write 2 to head
                                    swpab addi -1 swpab;  move L
                                     bri $erase_1__from_left;  goto erase_1__from_left
                                    .align
                                erase_1__from_left_case_0:
                                    popa swpab;  restore B from stack
                                    ldai {value} stab;  write 0 to head
                                    swpab addi 1 swpab;  move R
                                     bri $erase_1__check_left;  goto erase_1__check_left
                                    .align
                                .align
                                erase_1__check_left :
                                        swpab psha swpab;  save B to stack
                                        ldab addi -1;  B points to head
                                            brni $erase_1__check_left_case_0;  head is 0
                                            brzi $erase_1__check_left_case_1;  head is 1
                                            brzi $erase_1__check_left_case_2;  head is 2
                                    .alignerase_1__check_left_case_1:
                                        popa swpab;  restore B from stack
                                        ldai {value} stab;  write 0 to head
                                        swpab addi 1 swpab;  move R
                                         bri $erase_1__return_right;  goto erase_1__return_right
                                        .align
                                    .align
                                    erase_1__return_right :
                                            swpab psha swpab;  save B to stack
                                            ldab addi -1;  B points to head
                                                brni $erase_1__return_right_case_0;  head is 0
                                                brzi $erase_1__return_right_case_1;  head is 1
                                                brzi $erase_1__return_right_case_2;  head is 2
                                        .alignerase_1__return_right_case_1:
                                            popa swpab;  restore B from stack
                                            ldai {value} stab;  write 1 to head
                                            swpab addi 1 swpab;  move R
                                             bri $erase_1__return_right;  goto erase_1__return_right
                                            .align
                                        erase_1__return_right_case_2:
                                            popa swpab;  restore B from stack
                                            ldai {value} stab;  write 2 to head
                                            swpab addi 1 swpab;  move R
                                             bri $erase_1__return_right;  goto erase_1__return_right
                                            .align
                                        erase_1__return_right_case_0:
                                            popa swpab;  restore B from stack
                                            ldai {value} stab;  write 0 to head
                                            swpab addi -1 swpab;  move L
                                             bri $erase_1__check_1_on_right;  goto erase_1__check_1_on_right
                                            .align
                                        .align
                                        erase_1__check_1_on_right :
                                                swpab psha swpab;  save B to stack
                                                ldab addi -1;  B points to head
                                                    brni $erase_1__check_1_on_right_case_0;  head is 0
                                                    brzi $erase_1__check_1_on_right_case_1;  head is 1
                                                    brzi $erase_1__check_1_on_right_case_2;  head is 2
                                            .alignerase_1__check_1_on_right_case_1:
                                                popa swpab;  restore B from stack
                                                ldai {value} stab;  write 1 to head
                                                swpab addi 0 swpab;  move STAY
                                                 bri $erase_1__from_right;  goto erase_1__from_right
                                                .align
                                            erase_1__check_1_on_right_case_2:
                                                popa swpab;  restore B from stack
                                                ldai {value} stab;  write 2 to head
                                                swpab addi -1 swpab;  move L
                                                 bri $erase_1__check_1_on_left;  goto erase_1__check_1_on_left
                                                .align
                                            .align
                                            erase_1__check_1_on_left :
                                                    swpab psha swpab;  save B to stack
                                                    ldab addi -1;  B points to head
                                                        brni $erase_1__check_1_on_left_case_0;  head is 0
                                                        brzi $erase_1__check_1_on_left_case_1;  head is 1
                                                        brzi $erase_1__check_1_on_left_case_2;  head is 2
                                                .alignerase_1__check_1_on_left_case_2:
                                                    popa swpab;  restore B from stack
                                                    ldai {value} stab;  write 2 to head
                                                    swpab addi -1 swpab;  move L
                                                     bri $erase_1__check_1_on_left;  goto erase_1__check_1_on_left
                                                    .align
                                                erase_1__check_1_on_left_case_0:
                                                    popa swpab;  restore B from stack
                                                    ldai {value} stab;  write 1 to head
                                                    swpab addi 1 swpab;  move R
                                                     bri $init_erase_2;  goto init_erase_2
                                                    .align
                                                .align
                                                init_erase_2 :
                                                        swpab psha swpab;  save B to stack
                                                        ldab addi -1;  B points to head
                                                            brni $init_erase_2_case_0;  head is 0
                                                            brzi $init_erase_2_case_1;  head is 1
                                                            brzi $init_erase_2_case_2;  head is 2
                                                    .aligninit_erase_2_case_2:
                                                        popa swpab;  restore B from stack
                                                        ldai {value} stab;  write 2 to head
                                                        swpab addi 1 swpab;  move R
                                                         bri $init_erase_2;  goto init_erase_2
                                                        .align
                                                    init_erase_2_case_0:
                                                        popa swpab;  restore B from stack
                                                        ldai {value} stab;  write 0 to head
                                                        swpab addi -1 swpab;  move L
                                                         bri $erase_2__from_left;  goto erase_2__from_left
                                                        .align
                                                    .align
                                                    erase_2__from_left :
                                                            swpab psha swpab;  save B to stack
                                                            ldab addi -1;  B points to head
                                                                brni $erase_2__from_left_case_0;  head is 0
                                                                brzi $erase_2__from_left_case_1;  head is 1
                                                                brzi $erase_2__from_left_case_2;  head is 2
                                                        .alignerase_2__from_left_case_2:
                                                            popa swpab;  restore B from stack
                                                            ldai {value} stab;  write 0 to head
                                                            swpab addi 1 swpab;  move R
                                                             bri $erase_2__from_right;  goto erase_2__from_right
                                                            .align
                                                        .align
                                                        erase_2__from_right :
                                                                swpab psha swpab;  save B to stack
                                                                ldab addi -1;  B points to head
                                                                    brni $erase_2__from_right_case_0;  head is 0
                                                                    brzi $erase_2__from_right_case_1;  head is 1
                                                                    brzi $erase_2__from_right_case_2;  head is 2
                                                            .alignerase_2__from_right_case_0:
                                                                popa swpab;  restore B from stack
                                                                ldai {value} stab;  write 0 to head
                                                                swpab addi 1 swpab;  move R
                                                                 bri $erase_2__from_right;  goto erase_2__from_right
                                                                .align
                                                            erase_2__from_right_case_2:
                                                                popa swpab;  restore B from stack
                                                                ldai {value} stab;  write 0 to head
                                                                swpab addi -1 swpab;  move L
                                                                 bri $erase_2__return_left;  goto erase_2__return_left
                                                                .align
                                                            .align
                                                            erase_2__return_left :
                                                                    swpab psha swpab;  save B to stack
                                                                    ldab addi -1;  B points to head
                                                                        brni $erase_2__return_left_case_0;  head is 0
                                                                        brzi $erase_2__return_left_case_1;  head is 1
                                                                        brzi $erase_2__return_left_case_2;  head is 2
                                                                .alignerase_2__return_left_case_0:
                                                                    popa swpab;  restore B from stack
                                                                    ldai {value} stab;  write 0 to head
                                                                    swpab addi -1 swpab;  move L
                                                                     bri $erase_2__return_left;  goto erase_2__return_left
                                                                    .align
                                                                erase_2__return_left_case_2:
                                                                    popa swpab;  restore B from stack
                                                                    ldai {value} stab;  write 2 to head
                                                                    swpab addi 0 swpab;  move STAY
                                                                     bri $erase_2__from_left;  goto erase_2__from_left
                                                                    .align
                                                                erase_2__return_left_case_1:
                                                                    popa swpab;  restore B from stack
                                                                    ldai {value} stab;  write 0 to head
                                                                    swpab addi 1 swpab;  move R
                                                                     bri $erase_2__check_2_on_right;  goto erase_2__check_2_on_right
                                                                    .align
                                                                .align
                                                                erase_2__check_2_on_right :
                                                                        swpab psha swpab;  save B to stack
                                                                        ldab addi -1;  B points to head
                                                                            brni $erase_2__check_2_on_right_case_0;  head is 0
                                                                            brzi $erase_2__check_2_on_right_case_1;  head is 1
                                                                            brzi $erase_2__check_2_on_right_case_2;  head is 2
                                                                    .alignerase_2__check_2_on_right_case_0:
                                                                        popa swpab;  restore B from stack
                                                                        ldai {value} stab;  write 0 to head
                                                                        swpab addi 1 swpab;  move R
                                                                         bri $erase_2__check_2_on_right;  goto erase_2__check_2_on_right
                                                                        .align
                                                                    erase_2__check_2_on_right_case_1:
                                                                        popa swpab;  restore B from stack
                                                                        ldai {value} stab;  write 0 to head
                                                                        swpab addi 0 swpab;  move STAY
                                                                         bri $SUCCESS;  goto SUCCESS
                                                                        .align
                                                                    .align
                                                                    .align
                                                                    FAIL :
                                                                            ldai $FAIL_message
                                                                            ldai 0 sys halt
                                                                            .align
                                                                            FAIL_message :
                                                                                 "FAIL"
                                                                                .align
                                                                                SUCCESS :
                                                                                        ldai $SUCCESS_message
                                                                                        ldai 0 sys halt
                                                                                        .align
                                                                                        SUCCESS_message :
                                                                                             "SUCCESS"