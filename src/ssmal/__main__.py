import typing as T
import argparse
import sys

from ssmal.util.input_file_variant import InputFileVariant
from ssmal.vm1.vm import VM as VM1

parser = argparse.ArgumentParser()
parser.add_argument("-c", "--compile", action="store_true")
parser.add_argument("-m", "--machine", choices=["vm1"])
parser.add_argument("-r", "--run", action="store_true")
parser.add_argument("filename")
args = parser.parse_args(sys.argv[1:])

filename = T.cast(str, args.filename)

if args.machine == "vm1":
    vm = VM1()
else:
    raise Exception(f"Uknown machine specified: {args.machine}")
if args.compile:
    if not filename.endswith(InputFileVariant.suffix_map.assembler_file_suffix):
        raise RuntimeError(f"{filename} does not look like a ssmal assembler file - missing .al extension")
    vm.assemble(filename)
elif args.run:
    if not filename.endswith(InputFileVariant.suffix_map.object_file_suffix):
        raise RuntimeError(f"{filename} does not look like a ssmal object file - missing .bin extension")
    vm.run(filename)
else:
    raise RuntimeError(f"neither -compile nor -run specified")
