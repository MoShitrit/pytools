#!/usr/bin/env python
"""
This module contains the LocalExec class, which is used for local commands execution
"""

import subprocess
from color import Color
import os

__author__ = 'Moshe Shitrit'
__creation_date__ = '11/30/16'


class LocalExec:

    def __init__(self):
        pass

    @staticmethod
    def run_shell_cmd(cmd):
        """
        :param cmd: command to run
        :return: command output
        Run the cmd using subprocess.Popen method and return the output.
        """
        process = subprocess.Popen(cmd, shell=True,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        output = dict()
        output['ret_code'] = subprocess.Popen.wait(process)
        output['stdout'] = process.stdout.read().rstrip()
        output['stderr'] = process.stderr.read().rstrip()
        return output

    def is_root(self):
        """
        Check if the running user is root, using whoami command
        :return: True if root, False if not
        """
        if self.run_shell_cmd('whoami')['stdout'] != 'root':
            return False
        return True


