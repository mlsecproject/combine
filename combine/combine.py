#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import os
import sys

from baler import bale
from baler import tiq_output
from reaper import reap
from thresher import thresh
from winnower import winnow
# Combine components

__version__ = '0.1.4'


def main():
    possible_file_types = ['csv', 'json', 'crits']

    parser = argparse.ArgumentParser()
    parser.add_argument('--version', action='version', version='%(prog)s (version {0})'.format(__version__))
    parser.add_argument('-t', '--type', dest='file_type', choices=possible_file_types, default=possible_file_types[0],
                        help="Specify output file type.")
    parser.add_argument('-f', '--file', default=None, help="Specify output file. Defaults to harvest.FILETYPE")
    parser.add_argument('--output-dir', dest='output_dir', default='',
                        help="Specify output direction. Default to current directory")
    parser.add_argument('-d', '--delete', help="Delete intermediate files", action="store_true")
    parser.add_argument('-e', '--enrich', help="Enrich data", action="store_true")
    parser.add_argument('--tiq-test', help="Output in tiq-test format", action="store_true")
    args = parser.parse_args()

    if len(args.output_dir):
        if not os.path.isdir(args.output_dir):
            parser.print_usage()
            sys.exit('Output directory "{0}" does not exist.'.format(args.output_dir))

    def filepath(filename):
        return os.path.join(args.output_dir, filename)

    if args.file:
        out_filepath = filepath(args.file)
    else:
        out_filepath = filepath('harvest.' + args.file_type)

    harvest_filepath = filepath('harvest.json')
    crop_filepath = filepath('crop.json')
    enrich_filepath = filepath('enrich.json')
    enriched_filepath = filepath('enriched.' + args.file_type)

    reap(harvest_filepath)
    thresh(harvest_filepath, crop_filepath)
    bale(crop_filepath, out_filepath, args.file_type, True)

    if args.enrich or args.tiq_test:
        winnow(crop_filepath, crop_filepath, enrich_filepath)
        bale(enrich_filepath, enriched_filepath, args.file_type, False)

    if args.tiq_test:
        tiq_output(crop_filepath, enrich_filepath)

    if args.delete:
        # be careful with this when we support a JSON output type
        os.remove(harvest_filepath)
        os.remove(crop_filepath)
        os.remove(enrich_filepath)

if __name__ == "__main__":
    main()
