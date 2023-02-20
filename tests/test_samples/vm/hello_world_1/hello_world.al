.def hello 32
.def main 0

cali main
.goto main
    ldai hello
    psha
    ldai 0
    sys
    halt

.goto hello
"hello world!"
