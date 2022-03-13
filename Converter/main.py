#! /usr/bin/env python3
import tools.testbench as tb
import argparse
import logging as log
import subprocess as sub
import sys
import re


def run_tests_on_all():
    filenames = sub.run("basename -s .bt -a $(ls ../templates | grep -v - )",
                        shell=True,
                        stdout=sub.PIPE,
                        check=True)
    fns = filenames.stdout.decode().split("\n")[:-1:]
    p = re.compile(r'(\S+)_.*', re.VERBOSE)
    fns = [p.sub(r'\1', x) for x in fns]
    tb.run_multi_format_parse_test(fns, tb.resolve_test_input_by_format)


def convert_all():
    fmts = sub.run(
        'basename -s .ksy -a $(find kaitai_struct_formats -name "*.ksy")',
        shell=True,
        check=True,
        stdout=sub.PIPE)
    for fmt in fmts.stdout.decode().split("\n"):
        bp = tb.create_fmt_folder(fmt),
        conv = tb.call_converter(fmt, bp)
        tb.compile_parser(conv, bp, log.root)
        # TODO refine this


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--convert-only',
                        dest='run',
                        action='store',
                        nargs='?',
                        const=convert_all,
                        default=run_tests_on_all,
                        help="do only conversion")
    parser.add_argument('--log',
                        metavar='loglevel',
                        dest='log_lvl',
                        default='INFO',
                        nargs='?',
                        type=str)
    args = parser.parse_args(sys.argv[1:])
    numeric_level = getattr(log, args.log_lvl.upper(), 'INFO')
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: %s' % numeric_level)
    consoleLog = log.StreamHandler()
    logfile = log.FileHandler("testbench.log")
    logfile.setLevel(numeric_level)
    log.basicConfig(format='%(asctime)s::%(levelname)s:%(message)s',
                    level=numeric_level,
                    handlers=[consoleLog, logfile],
                    datefmt="%Y-%m-%d %H:%M:%S")
    args.run()


if __name__ == "__main__":
    main()
