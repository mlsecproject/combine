#!/usr/bin/env python

import argparse
import os
import sys
import logging

# Combine components
from logger import get_logger
from reaper import reap
from thresher import thresh
from baler import bale, tiq_output
from winnower import winnow

logger = get_logger()

parser = argparse.ArgumentParser()
parser.add_argument('-t', '--type', help="Specify output type. Currently supported: CSV and exporting to CRITs")
parser.add_argument('-f', '--file', help="Specify output file. Defaults to harvest.FILETYPE")
parser.add_argument('-d', '--delete', help="Delete intermediate files", action="store_true")
parser.add_argument('-e', '--enrich', help="Enrich data", action="store_true")
parser.add_argument('--tiq-test', help="Output in tiq-test format", action="store_true")
args = parser.parse_args()

possible_types = ['csv', 'json','crits']

if not args.type:
    out_type = 'csv'
elif args.type.lower() not in possible_types:
    sys.exit('Invalid file type specified. Possible types are: %s' % possible_types)
else:
    out_type = args.type.lower()

if args.file:
    out_file = args.file
else:
    out_file = 'harvest.'+out_type

base_path = os.path.dirname(__file__) + '/'
bp = base_path

reap(bp + 'harvest.json')
thresh(bp + 'harvest.json', bp + 'crop.json')
bale(bp + 'crop.json', out_file, out_type, True)

if args.enrich or args.tiq_test:
    winnow(bp + 'crop.json', bp + 'crop.json', bp +'enrich.json')
    bale(bp + 'enrich.json', bp + 'enriched.'+out_type, out_type, False)

if args.tiq_test:
    tiq_output(bp + 'crop.json', bp + 'enrich.json')

if args.delete:
    # be careful with this when we support a JSON output type
    os.remove(bp + 'harvest.json')
    os.remove(bp + 'crop.json')
    os.remove(bp + 'enrich.json')
