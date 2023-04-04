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
        ; no locals - otw create space on stack for locals
            ; stmt Expr stmt.lineno=3
                ; expr Call expr.lineno=3
                    ; expr Constant expr.lineno=3
                    ldai $z000_helloworld ; CONST str hello world
                psha  ldai 0 sys popa ; print()
        swpab ; save result
        ; clear stack
        popa swpab brb ; A <- result; return
        .align
        "Program.main()" .align
        
        .align
z000_helloworld: "hello world"
.align "HEAP START" .align
label_name_HEAP_START__0: .zeros 0x0220
.align "HEAP END" .align
allocator.malloc: ; Allocation function
psha ldai $label_name_HEAP_START__0 swpab ldab ; Current index
swpab ldai $label_name_HEAP_START__0 addi 0x20 addb psha ; return value (pointer)
popa swpab popa swpab psha swpab psha ; Rotate top of stack
ldai $label_name_HEAP_START__0 swpab ldab ; Current offset
swpab popa addb psha ; New offset
subi 200 muli -1 brni $label_name_die__2 ; die if too big
ldai $label_name_HEAP_START__0 swpab popa stab ; save new index
popa retn ; return, A <- pointer
label_name_die__2: halt
.zeros 0x20 .align ; a little space before stack.

