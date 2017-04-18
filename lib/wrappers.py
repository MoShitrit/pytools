#!/usr/bin/env python
"""
This module contains all the methods I use to init and wrap up scripts..
"""

import sys
import os
from datetime import datetime

import print_out
from local_exec import LocalExec

sys.path.insert(1, os.path.join(sys.path[0], 'lib'))
__author__ = 'Moshe Shitrit'
__creation_date__ = '1/5/16'


class Wrapper:
    def __init__(self, logger, log_file, script_user=None):
        self.logger = logger
        self.l_exec = LocalExec()
        self.script_user = script_user
        if not self.script_user:
            self.script_user = self.get_script_user()
        self.log_file = log_file

    def get_script_user(self):
        script_user = self.l_exec.run_shell_cmd('logname')['stdout']
        if script_user == 'root':
            script_user = raw_input('Please enter your username and hit [ENTER]: ')
            while self.l_exec.run_shell_cmd('getent passwd {0}'.format(script_user))['ret_code'] > 0 \
                    or script_user == 'root':
                script_user = raw_input('ERROR! The provided username does not exist in LDAP. Please try again: ')
        return script_user

    def init_script(self, title):
        """Print the welcome message, set the script_user for the log and write the first info line to the log.. """
        self.logger.info('{0} Script Started {0}'.format('=' * 33))
        print_out.banner('{0} Script. Log file will be written to {1}'.format(title, self.log_file))
        print_out.banner('Script started at {0}'.format(str(datetime.now())))
        self.logger.info('*** Run by user: {0} ***'.format(self.script_user))

    def end_script(self):
        print
        print_out.banner('Script done. Goodbye!')
        print_out.banner('Script ended at {0}'.format(str(datetime.now())))
        if self.logger:
            self.logger.info('=' * 35 + ' Script Ended ' + '=' * 35 + '\n')

    def terminate(self):
        if self.logger:
            self.logger.fatal('User hit CTRL + C, exiting script...')
        sys.exit(2)

    def terminate_ssh_auth_exception(self):
        print_out.print_func('SSH failed with Authentication Error. '
                             'Make sure you run the script as root and try again..',
                             logger=self.logger, level='error')
        exit(1)
