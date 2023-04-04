.goto 0 popa ldai 0x20 psha bri $Program.main ; start
.goto 0x20 halt ; exit
.goto 0x40 "TYPEINFO" .align
"int" .align
int.vtable:
"str" .align
str.vtable:
"Program" .align
Program.vtable:
    $Program.main
"int" .align
int.methods:
"str" .align
str.methods:
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

