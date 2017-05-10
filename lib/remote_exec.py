#!/usr/bin/env python
"""
This module contains the RemoteExec class, which is used for remote execution
using SSH, either regular or multi-threaded
"""

import getpass
import select
import socket
from Queue import Queue
from threading import Thread

import paramiko

from print_out import print_func
from local_exec import LocalExec

__author__ = 'Moshe Shitrit'
__creation_date__ = '1/5/16'


class RemoteExec:

    def __init__(self, args, wrapper):
        self.wrapper = wrapper
        self.logger = self.wrapper.logger
        self.args = args
        if 'batch' in self.args:
            self.q = Queue(maxsize=self.args.batch)
        self.l_exec = LocalExec()
        self.output = dict()
        if getattr(self.args, 'user'):
            self.user = self.args.user
        else:
            self.user = self.l_exec.run_shell_cmd('whoami')['stdout']
        self.logger.info('Username for SSH connection: {0}'.format(self.user))
        # if self.user != 'root':
        self.logger.info('Going to prompt for password for SSH connection..')
        self.passwd = getpass.unix_getpass('Please enter your password for SSH authentication: ')
        self.ldap_host = self.get_ldap_host()
        if self.ldap_host:
            print_func('Verifying credentials..', logger=self.logger)
            while not self.check_credentials():
                self.passwd = getpass.unix_getpass('ERROR: Incorrect password! Please try again: ')
            print_func('Credentials are valid!', logger=self.logger)
        else:
            print_func('No LDAP host was found! The script will continue without validating credentials',
                       logger=self.logger, level='warn')

        if 'batch' not in self.args:
            setattr(self.args, 'batch', 1)

    @staticmethod
    def set_ssh_client():
        """Define the SSH Client and set it to load the system host keys.."""
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        return ssh

    @staticmethod
    def check_ssh(node, logger):
        """Verify connectivity to a provided node via SSH.."""
        port = 22
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(10)
        try:
            logger.info('Verifying SSH connection to {0}..'.format(node))
            s.connect((node, port))
            s.shutdown(2)
            logger.info('Node {0} is accessible!'.format(node))
            return True
        except socket.error, paramiko.SSHException:
            logger.warning('Node {0} is NOT accessible!'.format(node))
            return False

    def get_ldap_host(self):
        """
        The function will read the file /etc/openldap/ldap.conf to get the 'uri' string from it.
        :return: ldap_host parameter, which is actually the hostname
        """
        self.logger.info('Getting LDAP host from /etc/openldap/ldap.conf')
        with open('/etc/openldap/ldap.conf', 'r') as ldap_conf:
            for line in ldap_conf.readlines():
                if 'uri' in line:
                    ldap_host = line
        try:
            ldap_host = ldap_host.split('//')[1].split('.')[0]
            self.logger.info('LDAP host found: {0}'.format(ldap_host))
            return ldap_host
        except UnboundLocalError:
            return False

    def check_credentials(self, dc_details='ou=Users,dc=foo,dc=bar'):
        """
        The function will use the username running the script (using 'logname' linux-native command).
        Then, it will fetch the running server's ldap_host by calling get_ldap_host function.
        Next, it will prompt the user to enter his/her password (using getpass lib to mask the input).
        Lastly, it will use Linux-native command 'ldapwhoami' to check if the provided password is valid.
        :return: True if password is valid or if no LDAP host is found, False if not.
        """
        print ''
        if self.ldap_host:
            cmd = 'ldapwhoami -vvv -h {0} -p 389 -D uid={1},{2} -x -w \'{3}\''.format(self.ldap_host,
                                                                                      self.user,
                                                                                      dc_details,
                                                                                      self.passwd)
            output = self.l_exec.run_shell_cmd(cmd)
            self.logger.info('ldapwhoami command result: {0}'.format(output))
            if output['ret_code'] != 0:
                return False
        return True

    def exec_func_threading(self, nodes, command):
        """
        :param nodes: list of nodes to execute the command on
        :param command: command to execute

        Run a command on a list of nodes simultaneously.
        Using standard-library modules Queue and Threading, build a queue and put the nodes in it.
        Then build a total number of threads that will match the args.batch size.
        Eventually, call the worker function that will call the actual exec func for each thread.
        """
        try:
            for node in nodes:
                self.q.put(node)
            for i in range(int(self.args.batch)):
                t = Thread(target=self.worker, args=(command,))
                t.daemon = True
                t.start()
            self.q.join()
        except KeyboardInterrupt:
            self.wrapper.terminate()

    def worker(self, command):
        """
        :param command: command to run

        Call the exec_func as long as the queue is not empty.
        """
        while self.q.not_empty:
            self.exec_func(self.q.get(), command)
            self.q.task_done()

    def exec_func(self, node, command, print_node=True, return_output=False):
        """
        :param node: Node on which to run the remote command.
        :param command: Command to run
        :param print_node: If True, the output printing will include the node_name in square brackets ([node])
        :param return_output: If True, out.readlines() is returned.
        :return out.readlines(): Return the command output as a list object (split by '\n') instead of printing it

        Run a command over SSH on a remote host
        """
        try:
            ssh = RemoteExec.set_ssh_client()
            self.logger.info('Connecting to {0} in order to run the command {1}...'.format(node, command))
            # if self.user == 'root':
            #     ssh.connect(node)
            # else:
            ssh.connect(node, username=self.user, password=self.passwd)
            channel = ssh.get_transport().open_session()
            channel.get_pty()
            out = channel.makefile()
            # if self.user == 'root':
            #     cmd = command
            # else:
            #     cmd = 'source /etc/profile; sudo {0}'.format(command)
            channel.exec_command(command)
            if print_node:
                self.output[node] = out.readlines()
                for line in self.output[node]:
                    print_func('[{0}]{1} {2}'.format(node, ' ' * (12 - len(node)), line.rstrip()), self.logger)
            elif return_output:
                return out.readlines()
            else:
                for line in out.readlines():
                        print_func(line.rstrip(), self.logger)
            ssh.close()

        except KeyboardInterrupt:
            self.wrapper.terminate()

        except paramiko.AuthenticationException:
            print_func('[{0}] SSH Failed with Authentication Exception! '
                       'Make sure you have access either with your credentials or with root'.format(node),
                       self.logger, 'error')

        except socket.error as e:
            print_func('[{0}] Node is not reachable! '
                       'SSH failed with error: {1}'.format(node, e.args[1]), self.logger, 'error')

        except paramiko.SSHException as e:
            print_func('[{0}] SSH failed with error: {1}'.format(node, e.message), self.logger, 'error')

    def exec_func_mco(self, mco_host, command, out_file=None):
        """
        :param mco_host:     MCollective host to connect to.
        :param command:      Command to run.
        :param out_file:     Redirect the command output to the provided file

        Get the mco_host and command to run,
        Connect by ssh to the mco_host and run the provided command.
        The output will be streamed to print_and_log function as long as exit_status is not ready
        """
        try:
            ssh = RemoteExec.set_ssh_client()
            self.logger.info('Command to run on MCollective node {0}: {1}'.format(mco_host, command))
            # if self.user == 'root':
            #     ssh.connect(mco_host)
            # else:
            ssh.connect(mco_host, username=self.user, password=self.passwd)
            channel = ssh.get_transport().open_session()
            channel.exec_command(command)
            if out_file:
                with open(out_file, 'a') as file_out:
                    while True:
                        if channel.exit_status_ready():
                            break
                        rl, wl, xl = select.select([channel], [], [], 0.0)
                        if len(rl) > 0:
                            file_out.write(channel.recv(10240))
                    file_out.write(channel.recv_stderr(10240))
            else:
                while True:
                    if channel.exit_status_ready():
                        break
                    rl, wl, xl = select.select([channel], [], [], 0.0)
                    if len(rl) > 0:
                        print_func(channel.recv(10240).rstrip(), self.logger)
                print_func(channel.recv_stderr(10240).rstrip(), self.logger)
            ssh.close()

        except KeyboardInterrupt:
            self.wrapper.terminate()

        except paramiko.AuthenticationException:
            print_func('[{0}] SSH Failed with Authentication Exception! '
                       'Make sure you have access either with your credentials or with root'.format(mco_host),
                       self.logger, 'error')

        except socket.error as e:
            print_func('[{0}] Node is not reachable! '
                       'SSH failed with error: {1}'.format(mco_host, e.args[1]), self.logger, 'error')

    def copy_file_sftp(self, remote_host, from_path, to_path):
        ssh = RemoteExec.set_ssh_client()
        if self.user == 'root':
            ssh.connect(remote_host)
        else:
            ssh.connect(remote_host, username=self.user, password=self.passwd)
            sftp = ssh.open_sftp()
            sftp.put(from_path, to_path)
            sftp.close()
            ssh.close()
