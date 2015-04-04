#! /usr/bin/env python
"""
"""
import argparse

parser = argparse.ArgumentParser(description="Nit")
subparsers = parser.add_subparsers()

init = subparsers.add_parser("init")
add = subparsers.add_parser("add")

args = parser.parse_args(["--help"])

print(args)
