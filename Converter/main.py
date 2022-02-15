#! /usr/bin/env python3
import tools.testbench  as tb
import argparse
import logging as log
import subprocess as sub
import sys



def run_tests_on_all():
    filenames = sub.run("basename -s .bt -a $(exa ../templates | grep -v - )",
            shell=True, stdout=sub.PIPE, check=True)
    tb.runMultiFromatParseTest(filenames.stdout.decode(), tb.resolveTestInputByFormat)

def convert_all():
    fmts = sub.run(
            'basename -s .ksy -a $(find kaitai_struct_formats -name "*.ksy")', 
            shell=True, check=True, stdout=sub.PIPE)
    for fmt in fmts.stdout.decode().split("\n"):
        conv = tb.callConverter(fmt)
        tb.compileParser(conv)
        #TODO refine this

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--convert-only',
            dest='run', 
            action='run_funct', 
            const=convert_all, 
            default=run_tests_on_all,
            help="do only conversion")
    args = parser.parse_args(sys.argv)
    args.run()


if __name__ == "__main__":
    main()
