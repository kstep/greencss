#!/usr/bin/python
# encoding: utf-8

from __future__ import with_statement

import sys, os
from greencss import convert

try:
    filename = os.path.abspath(sys.argv[1])
except IndexError:
    filename = None


if filename:
    if 'SERVER_NAME' in os.environ:  # CGI mode
        print "Content-Type: text/css\n"
        print '/*', filename, '*/'
    with open(filename, 'r') as f:
        data = f.read()
        #print data
        print convert(data)
else:
    # TODO: convert standard input
    pass

