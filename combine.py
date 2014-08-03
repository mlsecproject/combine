#!/usr/bin/env python

import argparse
import os
import sys

# Combine components
from reaper import reap
from thresher import thresh
from baler import bale

parser = argparse.ArgumentParser()
parser.add_argument('-t', '--type', help="Specify output type. Currently supported: CSV")
parser.add_argument('-f', '--file', help="Specify output file. Defaults to harvest.FILETYPE")
parser.add_argument('-d', '--delete', help="Delete intermediate files", action="store_true")
args = parser.parse_args()

possible_types = ['csv', 'CSV']

if not args.type:
    out_type = 'csv'
elif args.type not in possible_types:
    sys.exit('Invalid file type specified. Possible types are: %s' % possible_types)
else:
    out_type = args.type

if args.file:
    out_file = args.file
else:
    out_file = 'harvest.'+out_type

reap('harvest.json')
thresh('harvest.json', 'crop.json')
bale('crop.json', out_file, out_type)

# TODO: handle output requirements for tiq-test (cf. #29)

if args.delete:
    # be careful with this when we support a JSON output type
    os.remove('harvest.json')
    os.remove('crop.json')
