#!/usr/bin/env python
"""
This module contains the LocalExec class, which is used for local commands execution
"""

import subprocess
import platform

__author__ = 'Moshe Shitrit'
__creation_date__ = '11/30/16'


class LocalExec:

    def __init__(self, logger=None):
        self.distro = platform.dist()[0]
        self.logger = logger

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

    def install_package(self, package):
        """
        Install the provided package name using the appropriate package manager according to the distro
        :param package: name of package(s) to install
        :return: True if succeeded, False if not
        """
        if self.logger:
            self.logger.info('Going to install package(s): {0}'.format(package))
        if self.distro in ['centos', 'redhat']:
            if self.logger:
                self.logger.debug('OS distro is {0}, going to use yum package manager for installation'.format(self.distro))
            output = self.run_shell_cmd('sudo yum install -y {0}'.format(package))
        elif self.distro in ['Ubuntu', 'Debian']:
            if self.logger:
                self.logger.debug('OS distro is {0}, going to use apt package manager for installation'.format(self.distro))
            output = self.run_shell_cmd('sudo apt-get install -y {0}'.format(package))
        else:
            if self.logger:
                self.logger.error('OS distribution is not supported! Value for self.distro is: {0}'.format(self.distro))
            return False

        if output['ret_code'] != 0:
            if self.logger:
                self.logger.error('{0} package installation failed with error {1}: {2}'.format(package,
                                                                                               output['ret_code'],
                                                                                               output['stderr']))
            return False
        return True
