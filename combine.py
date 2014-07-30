#!/usr/bin/env python

# Combine components
from reaper import reap
from thresher import thresh
from baler import bale

reap('harvest.json')
thresh('harvest.json', 'crop.json')
bale('crop.json', 'harvest.csv', 'csv')
