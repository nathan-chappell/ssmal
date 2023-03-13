# fmt: off

class CompilerInternals:

    NOP     = "NOP"
    DBG     = "DBG"
    HALT    = "HALT"
    # arithmetic ops
    ADDB    = "ADDB"
    SUBB    = "SUBB"
    MULB    = "MULB"
    DIVB    = "DIVB"
    ADDi    = "ADDi"
    SUBi    = "SUBi"
    MULi    = "MULi"
    DIVi    = "DIVi"
    ADD_    = "ADD_"
    SUB_    = "SUB_"
    MUL_    = "MUL_"
    DIV_    = "DIV_"
    # data ops
    LDAi    = "LDAi"
    LDAb    = "LDAb"
    LDA_    = "LDA_"
    STAi    = "STAi"
    STAb    = "STAb"
    STA_    = "STA_"
    # stack ops
    PSHA    = "PSHA"
    POPA    = "POPA"
    CALi    = "CALi"
    CALA    = "CALA"
    CAL_    = "CAL_"
    RETN    = "RETN"
    # syscall - must be added later so that io can be put in...
    SYS     = "SYS"
    # register ops
    SWPAB   = "SWPAB"
    SWPAI   = "SWPAI"
    MOVSA   = "MOVSA"
    # branch ops
    BRi     = "BRi"
    BRa     = "BRa"
    BRZi    = "BRZi"
    BRNi    = "BRNi"
    BRZb    = "BRZb"
    BRNb    = "BRNb"

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

    def ZSTR(self, s: str) -> str: return f'"{s}"'
    def GOTO_LABEL(self, s: str) -> str: return f'${s}'
    def MARK_LABEL(self, s: str) -> str: return f'{s}:'
    def OFFSET(self, z: int) -> str: return f'{4 * z}'
