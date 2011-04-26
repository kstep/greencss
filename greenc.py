#!/usr/bin/python
# encoding: utf-8

from __future__ import with_statement

import sys  # , os
from greencss import convert

try:
    filename = sys.argv[1]
except IndexError:
    filename = None

if filename:
    with open(filename, 'r') as f:
        print convert(f.read())
else:
    # TODO: convert standard input
    pass

