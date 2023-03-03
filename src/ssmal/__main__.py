import argparse
import re
import sys
from typing import cast

from ssmal.util.input_file_variant import InputFileVariant
from ssmal.vm1.vm import VM as VM1

parser = argparse.ArgumentParser()
parser.add_argument("-c", "--compile", action="store_true")
parser.add_argument("-m", "--machine", choices=["vm1", "tm"])
parser.add_argument("-r", "--run", action="store_true")
parser.add_argument("-t", "--trace", action="store_true", default=False)
parser.add_argument("filename")
parser.add_argument("-i", "--input")
args = parser.parse_args(sys.argv[1:])

input_file = InputFileVariant(cast(str, args.filename))

if args.machine == "vm1":
    vm = VM1()
elif args.machine == "tm":
    vm = VM1()
    _input = cast(str | None, args.input)
    if _input is None:
        raise Exception(f"input is required for {args.machine=}")
    if not re.match(r'[12]+', _input):
        raise Exception(f"tm input must match [12]+")
    vm.compile_tm_lang(input_file)
    vm.assemble(input_file)
    vm.config.trace = args.trace
    vm.run_tm(input_file, _input)
    exit(0)
else:
    raise Exception(f"Unknown machine specified: {args.machine=}")

if args.compile:
    if input_file.is_assembler_file:
        vm.assemble(input_file)
    else:
        raise RuntimeError(f"{input_file.original_name} does not look like a ssmal assembler file - missing .al extension")
if args.run:
    vm.run(input_file)
