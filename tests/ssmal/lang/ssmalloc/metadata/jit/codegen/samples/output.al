.goto 0 popa ldai 0x20 psha bri $Program.main ; start
.goto 0x20 halt ; exit
.goto 0x40 "TYPEINFO" .align
"int" .align
int.vtable:
    .align
"str" .align
str.vtable:
    .align
"Summable" .align
Summable.vtable:
    $Summable.sum
    $Summable.add
    .align
"Pair" .align
Pair.vtable:
    $Pair.sum
    $Summable.add
    .align
"Triple" .align
Triple.vtable:
    $Triple.sum
    $Summable.add
    .align
"Program" .align
Program.vtable:
    $Program.main
    .align
"int" .align
int.methods:
"str" .align
str.methods:
"Summable" .align
Summable.methods:
    Summable.sum:
        ; no locals - otw create space on stack for locals
            ; stmt Return stmt.lineno=2
                ; expr Constant expr.lineno=2
                ldai 0 ; CONST int
        swpab ; save result
        popa ; clear stack
        popa swpab brb ; A <- result; return
        .align
        "Summable.sum()" .align
        
        .align
    Summable.add:
        ; no locals - otw create space on stack for locals
            ; stmt Return stmt.lineno=2
                ; expr BinOp expr.lineno=2
                    ; expr Call expr.lineno=2
                    ldai $label_name_return__5 psha ; save return address
                        ; expr Name expr.lineno=2
                            ; [access _location='self'] self _offset=2 mode='eval' self.push_count=1
                            lda_ 2
                    psha ; save self
                    movsa subi 4 swpab ldab ; A <- self
                    swpab ldab addi 0 swpab ldab ; A <- type_info.methods[index].code
                    bra ; goto sum
                    label_name_return__5:
                psha ; TOP <- left
                    ; expr Call expr.lineno=2
                    ldai $label_name_return__6 psha ; save return address
                        ; expr Name expr.lineno=2
                            ; [access _location='arg'] other _offset=2 mode='eval' self.push_count=2
                            lda_ 2
                    psha ; save self
                    movsa subi 4 swpab ldab ; A <- self
                    swpab ldab addi 0 swpab ldab ; A <- type_info.methods[index].code
                    bra ; goto sum
                    label_name_return__6:
                swpab popa  addb ; B <- right, A <- left
        swpab ; save result
        popa popa ; clear stack
        popa swpab brb ; A <- result; return
        .align
        "Summable.add(other)" .align
        
        .align
"Pair" .align
Pair.methods:
    Pair.sum:
        ; no locals - otw create space on stack for locals
            ; stmt Return stmt.lineno=2
                ; expr BinOp expr.lineno=2
                    ; expr Attribute expr.lineno=2
                        ; expr Name expr.lineno=2
                            ; [access _location='self'] self _offset=0 mode='eval' self.push_count=0
                            lda_ 0
                    addi 4 ; attribute x of value_type.name='Pair' mode='eval'
                    swpab ldab
                psha ; TOP <- left
                    ; expr Attribute expr.lineno=2
                        ; expr Name expr.lineno=2
                            ; [access _location='self'] self _offset=1 mode='eval' self.push_count=1
                            lda_ 1
                    addi 8 ; attribute y of value_type.name='Pair' mode='eval'
                    swpab ldab
                swpab popa  addb ; B <- right, A <- left
        swpab ; save result
        popa ; clear stack
        popa swpab brb ; A <- result; return
        .align
        "Pair.sum()" .align
        
        .align
"Triple" .align
Triple.methods:
    Triple.sum:
        ; no locals - otw create space on stack for locals
            ; stmt Return stmt.lineno=2
                ; expr BinOp expr.lineno=2
                    ; expr BinOp expr.lineno=2
                        ; expr Attribute expr.lineno=2
                            ; expr Name expr.lineno=2
                                ; [access _location='self'] self _offset=0 mode='eval' self.push_count=0
                                lda_ 0
                        addi 4 ; attribute x of value_type.name='Triple' mode='eval'
                        swpab ldab
                    psha ; TOP <- left
                        ; expr Attribute expr.lineno=2
                            ; expr Name expr.lineno=2
                                ; [access _location='self'] self _offset=1 mode='eval' self.push_count=1
                                lda_ 1
                        addi 8 ; attribute y of value_type.name='Triple' mode='eval'
                        swpab ldab
                    swpab popa  addb ; B <- right, A <- left
                psha ; TOP <- left
                    ; expr Attribute expr.lineno=2
                        ; expr Name expr.lineno=2
                            ; [access _location='self'] self _offset=1 mode='eval' self.push_count=1
                            lda_ 1
                    addi 12 ; attribute z of value_type.name='Triple' mode='eval'
                    swpab ldab
                swpab popa  addb ; B <- right, A <- left
        swpab ; save result
        popa ; clear stack
        popa swpab brb ; A <- result; return
        .align
        "Triple.sum()" .align
        
        .align
"Program" .align
Program.methods:
    Program.main:
        ldai 0 psha psha psha psha psha ; create space on stack for locals
            ; stmt AnnAssign stmt.lineno=3
                ; expr Call expr.lineno=3
                ldai 16
                cali $allocator.malloc
                swpab ldai $Triple.vtable stab swpab ; set vtable pointer
            swpab
                ; [access _location='local'] t _offset=4 mode='access' self.push_count=0
                movsa subi 20
            swpab stab
            ; stmt Assign stmt.lineno=4
                ; expr Constant expr.lineno=4
                ldai 3 ; CONST int
            psha
                ; expr Attribute expr.lineno=4
                    ; expr Name expr.lineno=4
                        ; [access _location='local'] t _offset=5 mode='eval' self.push_count=1
                        lda_ 5
                addi 4 ; attribute x of value_type.name='Triple' mode='access'
            swpab popa stab ; *TOP <- A
            ; stmt Assign stmt.lineno=5
                ; expr Constant expr.lineno=5
                ldai 4 ; CONST int
            psha
                ; expr Attribute expr.lineno=5
                    ; expr Name expr.lineno=5
                        ; [access _location='local'] t _offset=5 mode='eval' self.push_count=1
                        lda_ 5
                addi 8 ; attribute y of value_type.name='Triple' mode='access'
            swpab popa stab ; *TOP <- A
            ; stmt Assign stmt.lineno=6
                ; expr Constant expr.lineno=6
                ldai 5 ; CONST int
            psha
                ; expr Attribute expr.lineno=6
                    ; expr Name expr.lineno=6
                        ; [access _location='local'] t _offset=5 mode='eval' self.push_count=1
                        lda_ 5
                addi 12 ; attribute z of value_type.name='Triple' mode='access'
            swpab popa stab ; *TOP <- A
            ; stmt AnnAssign stmt.lineno=7
                ; expr Call expr.lineno=7
                ldai 12
                cali $allocator.malloc
                swpab ldai $Pair.vtable stab swpab ; set vtable pointer
            swpab
                ; [access _location='local'] p _offset=3 mode='access' self.push_count=0
                movsa subi 16
            swpab stab
            ; stmt Assign stmt.lineno=8
                ; expr Constant expr.lineno=8
                ldai 1 ; CONST int
            psha
                ; expr Attribute expr.lineno=8
                    ; expr Name expr.lineno=8
                        ; [access _location='local'] p _offset=4 mode='eval' self.push_count=1
                        lda_ 4
                addi 4 ; attribute x of value_type.name='Pair' mode='access'
            swpab popa stab ; *TOP <- A
            ; stmt Assign stmt.lineno=9
                ; expr Constant expr.lineno=9
                ldai 2 ; CONST int
            psha
                ; expr Attribute expr.lineno=9
                    ; expr Name expr.lineno=9
                        ; [access _location='local'] p _offset=4 mode='eval' self.push_count=1
                        lda_ 4
                addi 8 ; attribute y of value_type.name='Pair' mode='access'
            swpab popa stab ; *TOP <- A
            ; stmt AnnAssign stmt.lineno=10
                ; expr Call expr.lineno=10
                ldai $label_name_return__7 psha ; save return address
                    ; expr Name expr.lineno=10
                        ; [access _location='local'] p _offset=4 mode='eval' self.push_count=1
                        lda_ 4
                psha ; save self
                movsa subi 4 swpab ldab ; A <- self
                swpab ldab addi 0 swpab ldab ; A <- type_info.methods[index].code
                bra ; goto sum
                label_name_return__7:
            swpab
                ; [access _location='local'] p_sum _offset=2 mode='access' self.push_count=0
                movsa subi 12
            swpab stab
            ; stmt AnnAssign stmt.lineno=11
                ; expr Call expr.lineno=11
                ldai $label_name_return__8 psha ; save return address
                    ; expr Name expr.lineno=11
                        ; [access _location='local'] t _offset=5 mode='eval' self.push_count=1
                        lda_ 5
                psha ; save self
                movsa subi 4 swpab ldab ; A <- self
                swpab ldab addi 0 swpab ldab ; A <- type_info.methods[index].code
                bra ; goto sum
                label_name_return__8:
            swpab
                ; [access _location='local'] t_sum _offset=1 mode='access' self.push_count=0
                movsa subi 8
            swpab stab
            ; stmt AnnAssign stmt.lineno=12
                ; expr BinOp expr.lineno=12
                    ; expr Name expr.lineno=12
                        ; [access _location='local'] p_sum _offset=2 mode='eval' self.push_count=0
                        lda_ 2
                psha ; TOP <- left
                    ; expr Name expr.lineno=12
                        ; [access _location='local'] t_sum _offset=2 mode='eval' self.push_count=1
                        lda_ 2
                swpab popa  addb ; B <- right, A <- left
            swpab
                ; [access _location='local'] r_sum _offset=0 mode='access' self.push_count=0
                movsa subi 4
            swpab stab
            ; stmt Expr stmt.lineno=13
                ; expr Call expr.lineno=13
                    ; expr Name expr.lineno=13
                        ; [access _location='local'] r_sum _offset=0 mode='eval' self.push_count=0
                        lda_ 0
                psha  ldai 1 sys popa ; print()
        swpab ; save result
        popa popa popa popa popa ; clear stack
        popa swpab brb ; A <- result; return
        .align
        "Program.main()" .align
        
        .align
.align "HEAP START" .align
label_name_HEAP_START__0: .zeros 0x0120
.align "HEAP END" .align
allocator.malloc: ; Allocation function
psha ldai $label_name_HEAP_START__0 swpab ldab ; Current index
swpab ldai $label_name_HEAP_START__0 addi 0x20 addb psha ; return value (pointer)
popa swpab popa swpab psha swpab psha ; Rotate top of stack
ldai $label_name_HEAP_START__0 swpab ldab ; Current offset
swpab popa addb psha ; New offset
subi 100 muli -1 brni $label_name_die__10 ; die if too big
ldai $label_name_HEAP_START__0 swpab popa stab ; save new index
popa retn ; return, A <- pointer
label_name_die__10: halt
.zeros 0x20 .align ; a little space before stack.

