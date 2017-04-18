#!/usr/bin/env python
"""
This script contains all functions that are related to files handling
"""

from color import Color

__author__ = 'Moshe Shitrit'
__creation_date__ = '1/5/16'


def convert_file_to_list(f):
    """
    :param f: Text file that contains a list of nodes

    Convert f to a list and return the list
    """
    try:
        with open(f) as nodes:
            nodes_list = list()
            for node in nodes.read().splitlines():
                if node:
                    nodes_list.append(node.rstrip(' '))
        return nodes_list
    except IOError:
        print '{0}{1}ERROR: File {2} does not exist! ' \
              'Please verify the path and try again..{3}'.format(Color.BOLD, Color.RED, f, Color.END)
        exit(4)

