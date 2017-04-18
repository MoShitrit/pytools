#!/usr/bin/env python
"""
This module contains a class named 'Color', from which it is possible to apply
styling on certain lines to print.
"""

__author__ = 'Moshe Shitrit'
__creation_date__ = '12/13/15'


class Color:
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

    def __init__(self):
        pass
