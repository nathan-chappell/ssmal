
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
        .align

    reading_ones_case_0:
        ; restore b
        popa swpab
        ; write value
        ldai 0 stab
        ; move R
        swpab addi 1 swpab
        ; goto state
        bri $FAIL .align 

    reading_ones_case_1:
        ; restore b
        popa swpab
        ; write value
        ldai 0 stab
        ; move R
        swpab addi 1 swpab
        ; goto state
        bri $reading_ones .align 

    reading_ones_case_2:
        ; restore b
        popa swpab
        ; write value
        ldai 0 stab
        ; move R
        swpab addi 1 swpab
        ; goto state
        bri $reading_twos .align 

        .align
reading_twos:
    ; save B
    swpab psha swpab
    ; B points to position on tape
    ldab addi -1
        ; if 0
        brni $reading_twos_case_0
        ; if 1
        brzi $reading_twos_case_1
        ; else
        bri $reading_twos_case_2
        .align

    reading_twos_case_0:
        ; restore b
        popa swpab
        ; write value
        ldai 0 stab
        ; move R
        swpab addi 1 swpab
        ; goto state
        bri $SUCCESS .align 

    reading_twos_case_1:
        ; restore b
        popa swpab
        ; write value
        ldai 0 stab
        ; move R
        swpab addi 1 swpab
        ; goto state
        bri $FAIL .align 

    reading_twos_case_2:
        ; restore b
        popa swpab
        ; write value
        ldai 0 stab
        ; move R
        swpab addi 1 swpab
        ; goto state
        bri $reading_twos .align 

        .align
.align
FAIL:
    ldai $fail_message
    psha
    ldai 0
    sys
    halt
    .align
    fail_message: "FAIL"

.align
SUCCESS:
    ldai $success_message
    psha
    ldai 0
    sys
    halt
    .align
    success_message: "SUCCESS"
