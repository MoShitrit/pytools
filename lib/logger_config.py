#!/usr/bin/env python

import logging
import logging.handlers
import os
import sys

from print_out import print_func

__author__ = 'Moshe Shitrit'
__creation_date__ = '12/10/15'


class MyLogger:

    def __init__(self, script_name, level=logging.INFO):

        # Confirm that logs folder exists and create it if not
        self.logs_dir = '{0}/logs'.format(sys.path[0])
        if not os.path.exists(self.logs_dir):
            os.makedirs(self.logs_dir)
        log_name = 'log_{0}'.format(script_name.split('/')[-1].replace('.py', '.log'))
        self.log_file = '{0}/{1}'.format(self.logs_dir, log_name)
        try:
            self.logger = logging.getLogger(__name__)
            self.check_rotate_log()
            logging.basicConfig(filename=self.log_file, level=level,
                                format='%(asctime)s  %(levelname)s: %(message)s')
            try:
                os.chmod(self.log_file, 0777)
            except OSError:
                pass

        except IOError:
            print_func("No permissions to access the log file! "
                       "Please make sure you have write access to the log file "
                       "(running the script with sudo will also do the trick)..\n", level='error')
            exit(2)

    def get_logger(self):
        return self.logger

    def check_rotate_log(self):
        rotate_handler = logging.handlers.RotatingFileHandler(
            self.log_file, maxBytes=5242880, backupCount=5)
        self.logger.addHandler(rotate_handler)
        self.logger.info('')
        self.logger.removeHandler(rotate_handler)
