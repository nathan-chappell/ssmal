import ast
import argparse
import pprint
import sys

from simpletypes.simple_ast.simple_ast_parser import parse_Program
from simpletypes.typechecker.typechecker import TypeChecker

argument_parser = argparse.ArgumentParser()
argument_parser.add_argument("filename")
argument_parser.add_argument("-p", "--print-ast", action="store_true")
argument_parser.add_argument("-t", "--type-check", action="store_true")

args = argument_parser.parse_args(sys.argv[1:])


with open(args.filename) as f:
    source_code = f.read()
    program = parse_Program(compile(source_code, args.filename, "exec", ast.PyCF_ONLY_AST))
    if args.print_ast:
        pprint.pprint(program)
    if args.type_check:
        type_checker = TypeChecker()
        if type_checker.check(program):
            print("type-checking completed successfully.")
        else:
            print("type-checking failed.")
