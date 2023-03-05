FAIL:
    .def fail_message "FAIL"
    ldai fail_message
    psha
    sys 0
    halt

SUCCESS:
    .def success_message "SUCCESS"
    ldai success_message
    psha
    sys 0
    halt

reading_ones:
    ; save B
    swpab psha swpab
    ; B points to position on tape
    ldab addi -1
        ; if 0
        brni $reading_ones_case_0
        ; if 1
        brzi $reading_ones_case_1
        ; else
        bri $reading_ones_case_2
    
    reading_ones_case_0:
        bri SUCCESS

    reading_ones_case_1:
        ; restore b
        popa swpab
        ; write 0
        stai 0 stab
        ; move right
        swpab addi 4 swpab
        ; goto state reading_ones
        bri $reading_ones
    
    reading_ones_case_2:
        ; restore b
        popa swpab
        ; write 0
        stai 0 stab
        ; move right
        swpab addi 4 swpab
        ; goto state reading_twos
        bri $reading_twos

reading_twos:
    ; save B
    swpab psha swpab
    ; B points to position on tape
    ldab addi -1
        ; if 0
        brni $SUCCESS
        ; if 1
        brzi $FAIL
        ; else
        bri $reading_twos_case_2

    reading_twos_case_2:
        ; restore b
        popa swpab
        ; write 0
        stai 0 stab
        ; move right
        swpab addi 4 swpab
        ; goto state reading_twos
        bri $reading_twos