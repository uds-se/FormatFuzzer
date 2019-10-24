#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""
Run pfp on input data using a specified 010 Editor template for parsing
"""


import argparse
import os
import pfp
import sys


def parse_args(argv):
    parser = argparse.ArgumentParser("pfp", description=__doc__)

    parser.add_argument(
        "-t", "--template",
        required=True,
        help="The template to parse with",
    )

    parser.add_argument(
        "-k", "--keep",
        default=False,
        action="store_true",
        help="Keep successfully parsed data on error",
    )

    parser.add_argument(
        "input",
        type=argparse.FileType("rb"),
        default=sys.stdin,
        help="The input data stream or file to parse. Use '-' for piped data",
    )

    return parser.parse_args(argv[1:])


def main(argv=None):
    """Main function for this script

    :argv: TODO
    :returns: TODO
    """
    if argv is None:
        argv = sys.argv

    args = parse_args(argv)
    dom = pfp.parse(
        template_file=args.template,
        data=args.input,
        keep_successful=args.keep,
    )
    print(dom._pfp__show())


if __name__ == "__main__":
    main(sys.argv)
