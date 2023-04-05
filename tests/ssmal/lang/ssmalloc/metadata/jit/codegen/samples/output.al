.goto 0 popa ldai 0x20 psha bri $Program.main ; start
.goto 0x20 halt ; exit
.goto 0x40 "TYPEINFO" .align
"int" .align
int.vtable:
"str" .align
str.vtable:
"Pair" .align
Pair.vtable:
    $Pair.sum
"Program" .align
Program.vtable:
    $Program.main
"int" .align
int.methods:
"str" .align
str.methods:
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
"Program" .align
Program.methods:
    Program.main:
        ldai 0 psha ; create space on stack for locals
            ; stmt AnnAssign stmt.lineno=3
                ; expr Call expr.lineno=3
                ldai 12
                cali $allocator.malloc
            swpab
                ; [access _location='local'] p _offset=0 mode='access' self.push_count=0
                movsa subi 4
            swpab stab
            ; stmt Assign stmt.lineno=4
                ; expr Constant expr.lineno=4
                ldai 1 ; CONST int
            psha
                ; expr Attribute expr.lineno=4
                    ; expr Name expr.lineno=4
                        ; [access _location='local'] p _offset=1 mode='eval' self.push_count=1
                        lda_ 1
                addi 4 ; attribute x of value_type.name='Pair' mode='access'
            swpab popa stab ; *TOP <- A
            ; stmt Assign stmt.lineno=5
                ; expr Constant expr.lineno=5
                ldai 2 ; CONST int
            psha
                ; expr Attribute expr.lineno=5
                    ; expr Name expr.lineno=5
                        ; [access _location='local'] p _offset=1 mode='eval' self.push_count=1
                        lda_ 1
                addi 8 ; attribute y of value_type.name='Pair' mode='access'
            swpab popa stab ; *TOP <- A
            ; stmt Expr stmt.lineno=6
                ; expr Call expr.lineno=6
                    ; expr Call expr.lineno=6
                    pshi ; save return address
                        ; expr Name expr.lineno=6
                            ; [access _location='local'] p _offset=1 mode='eval' self.push_count=1
                            lda_ 1
                    psha ; save self
                    movsa subi 4 swpab ldab ; A <- self
                    swpab ldab addi 0 swpab ldab ; A <- type_info.methods[index].code
                    bra ; goto sum
                psha  ldai 1 sys popa ; print()
        swpab ; save result
        popa ; clear stack
        popa swpab brb ; A <- result; return
        .align
        "Program.main()" .align
        
        .align
.align "HEAP START" .align
label_name_HEAP_START__0: .zeros 0x0060
.align "HEAP END" .align
allocator.malloc: ; Allocation function
psha ldai $label_name_HEAP_START__0 swpab ldab ; Current index
swpab ldai $label_name_HEAP_START__0 addi 0x20 addb psha ; return value (pointer)
popa swpab popa swpab psha swpab psha ; Rotate top of stack
ldai $label_name_HEAP_START__0 swpab ldab ; Current offset
swpab popa addb psha ; New offset
subi 40 muli -1 brni $label_name_die__2 ; die if too big
ldai $label_name_HEAP_START__0 swpab popa stab ; save new index
popa retn ; return, A <- pointer
label_name_die__2: halt
.zeros 0x20 .align ; a little space before stack.

