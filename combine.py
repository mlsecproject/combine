#!/usr/bin/env python

import argparse
import os

# Combine components
from reaper import reap
from thresher import thresh
from baler import bale

parser = argparse.ArgumentParser()
parser.add_argument('-t', '--type', help="Specify output type. Currently supported: CSV")
parser.add_argument('-f', '--file', help="Specify output file. Defaults to harvest.FILETYPE")
parser.add_argument('-d', '--delete', help="Delete intermediate files", action="store_true")
args = parser.parse_args()

reap('harvest.json')
thresh('harvest.json', 'crop.json')
if not args.type:
    out_type = 'csv'
elif args.type not in ['csv']:
    raise
else:
    out_type = args.type

if args.file:
    out_file = args.file
else:
    out_file = 'harvest.'+out_type

bale('crop.json', out_file, out_type)

if args.delete:
    os.remove('harvest.json')
    os.remove('crop.json')
