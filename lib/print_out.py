#!/usr/bin/env python
"""
This module contains all the methods I use to print outputs to the user..
"""

from color import Color

__author__ = 'Moshe Shitrit'
__creation_date__ = '1/5/16'


def banner(message, border='-'):
    """Get a message as an argument, print it with borders.."""
    line = '+' + border * (len(message) + 2) + '+'
    print (line)
    print ('| ' + message + ' |')
    print (line)


def print_func(message, logger=None, level='info', as_banner=False):
    if logger:
        levels = {'debug': logger.debug,
                  'info': logger.info,
                  'warn': logger.warning,
                  'error': logger.error,
                  'critical': logger.critical}
        levels[level](message)

    formatting = {'info': '{0}'.format(message),
                  'warn': '{0}{1}WARNING: {2}{3}'.format(Color.BOLD, Color.YELLOW, message, Color.END),
                  'error': '{0}{1}ERROR: {2}{3}'.format(Color.BOLD, Color.RED, message, Color.END),
                  'critical': '{0}{1}CRITICAL: {2}{3}'.format(Color.BOLD, Color.RED, message, Color.END)}
    if as_banner:
        banner(message)
    else:
        print (formatting[level])
