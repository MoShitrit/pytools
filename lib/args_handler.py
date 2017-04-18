#!/usr/bin/env python
"""
This module contains all the Argument handling methods and classes..
"""

import argparse
import sys

__author__ = 'Moshe Shitrit'
__creation_date__ = '12/10/15'


class MyParser(argparse.ArgumentParser):

    def error(self, message):
        self.print_help()
        sys.stderr.write('\nERROR: %s\n\n' % message)
        sys.exit(2)

    def add_nodes_arg(self, **kwargs):
        if 'help' in kwargs:
            self.add_argument('--nodes', '-N', **kwargs)
        else:
            self.add_argument('--nodes', '-N',
                              help='Path to a text file containing a list of nodes to process. '
                                   'If this argument is passed, all other arguments will be ignored, '
                                   'i.e. /tmp/nodes.txt',
                              **kwargs)

    def add_hosts_arg(self, **kwargs):
        if 'help' in kwargs:
            self.add_argument('--hosts', '-H', **kwargs)
        else:
            self.add_argument('--hosts', '-H',
                              help='Hostnames to process, you may enter more than one, '
                                   'using "," as the field separator, i.e. node1,node2 etc.. (NO SPACES!!)',
                              **kwargs)

    def add_initd_arg(self, **kwargs):
        self.add_argument('--initd',
                          help='Linux service name to process', **kwargs)

    def add_batch_args(self, batch=1, batch_sleep=0, **kwargs):
        self.add_argument('--batch',
                          help='Do requests in batches. Defaults to {0}'.format(batch),
                          type=int, default=batch, **kwargs)

        self.add_argument('--batch_sleep',
                          help='Sleep time between batches (in seconds). Defaults to {0}'.format(batch_sleep),
                          type=int, default=batch_sleep, **kwargs)

    def generate_args(self):
        """
        Parse all the added arguments and return it to the calling script..
        If no arguments were passed to the script- the function will print the help doc and exit with error code.
        """

        if len(sys.argv) == 1:
            self.print_help()
            print '\n\nERROR: No arguments passed!\n'
            sys.exit(3)

        return self.parse_args()

    def log_args(self, logger):
        """Log all the arguments that were provided by the user"""
        logger.info('{0} Arguments Provided {0}'.format('='*7))
        for arg in vars(self.parse_args()):
            if getattr(self.parse_args(), arg):
                logger.info('{0}: {1}'.format(str.upper(arg), getattr(self.parse_args(), arg)))
        logger.info('{0} End of Arguments {0}'.format('='*8))
