# fmt: off

class CompilerInternals:

    NOP     = "nop"
    DBG     = "dbg"
    HALT    = "halt"
    # arithmetic ops
    ADDB    = "addb"
    SUBB    = "subb"
    MULB    = "mulb"
    DIVB    = "divb"
    ADDi    = "addi"
    SUBi    = "subi"
    MULi    = "muli"
    DIVi    = "divi"
    ADD_    = "add_"
    SUB_    = "sub_"
    MUL_    = "mul_"
    DIV_    = "div_"
    # data ops
    LDAi    = "ldai"
    LDAb    = "ldab"
    LDA_    = "lda_"
    STAi    = "stai"
    STAb    = "stab"
    STA_    = "sta_"
    # stack ops
    PSHA    = "psha"
    POPA    = "popa"
    CALi    = "cali"
    CALA    = "cala"
    CAL_    = "cal_"
    RETN    = "retn"
    # syscall - must be added later so that io can be put in...
    SYS     = "sys"
    # register ops
    SWPAB   = "swpab"
    SWPAI   = "swpai"
    MOVSA   = "movsa"
    # branch ops
    BRi     = "bri"
    BRa     = "bra"
    BRb     = "brb"
    BRZi    = "brzi"
    BRNi    = "brni"
    BRZb    = "brzb"
    BRNb    = "brnb"

    NULL_TERMINATOR = b'\x00'
    NONE = f'{0}'
    FALSE = f'{0}'
    TRUE = f'{1}'

    BYTE_ORDER = 'little'

    PTOPz = 0  # print top of stack as null-terminated string
    PTOPi = 1  # print top of stack as decimal integer
    PTOPx = 2  # print top of stack as 4-byte int in hex (le - probably)
    PREG = 3  # print registers
    PMEM = 4  # dump memory

    def COMMENT(self, s: str) -> str:       return f'; {s}'
    def GOTO_LABEL(self, s: str) -> str:    return f'${s}'
    def MARK_LABEL(self, s: str) -> str:    return f'{s}:'
    def OFFSET(self, z: int) -> str:        return f'{4 * z}'
    def ZSTR(self, s: str) -> str:          return f'"{s}"'

    # Macros

    
    def FOLLOW_A(self) -> str:  return f'{self.SWPAB} {self.LDAb}'

    def LINE(self, *instructions: str, comment: str = None, alignment=40) -> str:
        instructions_str = ' '.join(instructions)
        comment_str = f'; {comment}' if comment is not None else ""
        alignment_str = ' '*(alignment - len(instructions_str))
        return instructions_str + alignment_str + comment_str #  + "\n"
