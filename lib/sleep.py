#!/usr/bin/env python
"""
This module contains a script func to use in certain scenarios..
"""

import sys
import time

__author__ = 'Moshe Shitrit'
__creation_date__ = '1/5/16'


def sleep_func(sleep_time):
    """Get the sleep time (in seconds) as an argument and sleep for this amount of seconds.."""
    print '\n{0} Sleeping for {1} seconds {0} '.format('='*30, str(sleep_time))
    for i in xrange(sleep_time, 0, -1):
        time.sleep(1)
        sys.stdout.write(str(i) + ' ')
        sys.stdout.flush()
    print
    print '='*85 + '\n'
