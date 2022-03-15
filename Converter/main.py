#! /usr/bin/env python3
import argparse
import logging as log
import sys
from os import listdir, walk
import os.path as path
import tools.testbench as tb


def run_tests_on_all(logger, file_path, file_names=None):
    log.info("=== Running tests on the formats specified below ===")
    if file_names is not None:
        log.info(f"formats to be run: {file_names}")
        file_path = file_path if file_path is not None else tb.TEST_FILE_ROOT
        tb.run_multi_format_parse_test(file_names, tb.provide_wild_files(file_path), logger)
    else:
        files = listdir(file_path)
        log.info(f"formats to be run: {files}")
        tb.run_multi_format_parse_test(files, tb.provide_wild_files(file_path), logger)


def convert_all(logger, file_path, file_names=None):
    log.info("=== Converting and compiling all templates ===")
    for root, _, files in walk(tb.KAITAI_BASE_PATH):
        for file in filter(lambda f: f.endswith("ksy"), files):
            try:
                base_path = tb.create_fmt_folder(file.rsplit(".", 1)[0])
                converted = tb.call_converter(path.join(root, file), file.rsplit(".", 1)[0], base_path, logger)
                tb.compile_parser(converted, base_path, True)
            except tb.TestRunException as e:
                log.error("Error occurred while transpiling templates")
                e.print()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('file_path',
                        nargs='?',
                        type=str,
                        default=tb.TEST_FILE_ROOT,
                        help='the path for finding test files')
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
    parser.add_argument('--formats',
                        dest='formats',
                        nargs='+',
                        type=str,
                        default=None,
                        help='The formats to run tests on')
    parser.add_argument('--filter-diffs', action='store_true', dest="filter_diffs",
                        help='filter "useless" diffs')
    parser.add_argument('--no-filter-diffs', action='store_false', dest="filter_diffs",
                        help='do not filter "useless" diffs')
    parser.set_defaults(filter_diffs=True)
    args = parser.parse_args(sys.argv[1::])
    numeric_level = getattr(log, args.log_lvl.upper(), 'INFO')
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: %s' % numeric_level)
    logger = tb.set_up_logger(numeric_level)
    print(logger.handlers)
    args.run(logger, args.file_path, args.formats)


if __name__ == "__main__":
    main()
