reading_ones:

    swpab psha swpab              ;  save B to stack
    ldab addi -1                  ;  B points to head
        brni $reading_ones_case_0     ;  head is 0
        brzi $reading_ones_case_1     ;  head is 1
        bri $reading_ones_case_2      ;  head is 2
        
        .align
    
    reading_ones_name: "reading_ones"
    reading_ones_case_0:
        popa swpab                    ;  restore B from stack
        ldai 0 stab                   ;  write 0 to head
        swpab addi 4 swpab            ;  move R
        bri $FAIL                     ;  goto FAIL
        
        .align
    reading_ones_case_1:
        popa swpab                    ;  restore B from stack
        ldai 0 stab                   ;  write 0 to head
        swpab addi 4 swpab            ;  move R
        bri $reading_ones             ;  goto reading_ones
        
        .align
    reading_ones_case_2:
        popa swpab                    ;  restore B from stack
        ldai 0 stab                   ;  write 0 to head
        swpab addi 4 swpab            ;  move R
        bri $reading_twos             ;  goto reading_twos
        
        .align

.align
                              ;  end of reading_ones


reading_twos:

    swpab psha swpab              ;  save B to stack
    ldab addi -1                  ;  B points to head
        brni $reading_twos_case_0     ;  head is 0
        brzi $reading_twos_case_1     ;  head is 1
        bri $reading_twos_case_2      ;  head is 2
        
        .align
    
    reading_twos_name: "reading_twos"
    reading_twos_case_0:
        popa swpab                    ;  restore B from stack
        ldai 0 stab                   ;  write 0 to head
        swpab addi 4 swpab            ;  move R
        bri $SUCCESS                  ;  goto SUCCESS
        
        .align
    reading_twos_case_1:
        popa swpab                    ;  restore B from stack
        ldai 0 stab                   ;  write 0 to head
        swpab addi 4 swpab            ;  move R
        bri $FAIL                     ;  goto FAIL
        
        .align
    reading_twos_case_2:
        popa swpab                    ;  restore B from stack
        ldai 0 stab                   ;  write 0 to head
        swpab addi 4 swpab            ;  move R
        bri $reading_twos             ;  goto reading_twos
        
        .align

.align
                              ;  end of reading_twos


.align
FAIL:
    ldai $FAIL_message psha
    ldai 0 sys halt
    .align
    FAIL_message: "FAIL"


.align
SUCCESS:
    ldai $SUCCESS_message psha
    ldai 0 sys halt
    .align
    SUCCESS_message: "SUCCESS"
