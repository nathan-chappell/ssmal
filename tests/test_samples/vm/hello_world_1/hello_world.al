.def hello 32
.def main 8

cali main
.goto main
    ldai hello
    psha
    ldai 0
    sys

.goto hello
"hello world!"
