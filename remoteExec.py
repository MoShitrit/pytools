#!/usr/bin/env python

""" Script for remote execution """

from lib.wrappers import Wrapper
from lib.args_handler import MyParser
from lib.logger_config import MyLogger
from lib.remote_exec import RemoteExec
from lib.print_out import print_func
from lib.prompts import confirm
from lib.file_handler import convert_file_to_list
from lib.color import Color
from lib import sleep

__author__ = 'Moshe Shitrit'
__creation_date__ = '4/17/17'

# Build the argument parser
parser = MyParser(description=__doc__)
parser.add_hosts_arg()
parser.add_nodes_arg()
parser.add_batch_args()
cmd_or_script = parser.add_mutually_exclusive_group(required=True)
cmd_or_script.add_argument('--cmd', help='The command to run on remote nodes')
cmd_or_script.add_argument('--script', help='Path to script that will be executed locally on the destination host(s)')
parser.add_argument('--user', '-u', help='User for SSH authentication')
args = parser.generate_args()

# Build the logger
my_log = MyLogger(__file__)
logger = my_log.get_logger()

# Build the script wrapper
wrapper = Wrapper(logger, my_log.log_file)


# ================== END GLOBAL ================== #


def generate_nodes_list():
    """
    Generate the list of nodes which was provided either via ..
    """
    if args.nodes:
        nodes_list = convert_file_to_list(args.nodes)
    else:
        nodes_list = []
        for node in args.hosts.split(","):
            if node:
                nodes_list.append(node)

    logger.info('*** NODES LIST TO PROCESS: ***')
    print '{0}{1}{2}NODES LIST TO PROCESS:{3}'.format(Color.BOLD, Color.UNDERLINE, Color.BLUE, Color.END)
    for node in nodes_list:
        print_func(node, logger=logger, level='info')
    print
    print_func('*** END OF NODES LIST ***', logger=logger, level='info')
    print
    return nodes_list


def iterate_nodes_and_call_exec_func(r_exec, nodes, script_src_path=None):
    """
    Get the r_exec object and the list of nodes as arguments.
    Create an additional list called "work" which will append the amount of nodes
    equal to the provided batch argument. If batch_sleep argument was provided,
    it will sleep x seconds between each batch.
    """
    command = get_command()
    work = list()
    count = 0
    for node in nodes:
        count += 1
        work.append(node)
        if len(work) == int(args.batch):
            r_exec.exec_func_threading(nodes=work, command=command, script_src_path=script_src_path)
            count = 0
            if args.batch_sleep > 0 and count < (len(nodes) - len(work)):
                logger.info('*** Sleeping for %d seconds before moving on to next batch ***',
                            args.batch_sleep)
                sleep.sleep_func(args.batch_sleep)
            work = list()
    if len(work) > 0:
        r_exec.exec_func_threading(nodes=work, command=command)


def get_command():
    """
    Check which argument was passed, cmd or script.
    :return: either command to run or the script path on destination node (/tmp/<script_name>) 
    """
    if getattr(args, 'script'):
        return '/tmp/{0}'.format(args.script.split('/')[-1])
    else:
        return args.cmd


def execute_script(nodes):
    """
    First, copy the provided script to the list of nodes (to /tmp path).
    Then - run the script locally.
    Eventually - delete the script from /tmp, to cleanup the leftovers.
    :param nodes: List of nodes to which the script will be copied and on which it will be executed
    """
    if confirm('run the script {0} on multiple servers'.format(args.script), wrapper=wrapper,
               title='running script {0}'.format(args.script)):
        r_exec = RemoteExec(args=args, wrapper=wrapper)
        iterate_nodes_and_call_exec_func(r_exec, nodes, script_src_path=args.script)


def execute_cmd(nodes):
    """
    Call remote_exec function to run the provided cmd on the list of nodes
    :param nodes: List of nodes on which the shell command will be executed
    """
    if confirm('run {0} command on multiple servers'.format(args.cmd), wrapper=wrapper,
               title='running {0} command'.format(args.cmd)):
        r_exec = RemoteExec(args=args, wrapper=wrapper)
        iterate_nodes_and_call_exec_func(r_exec, nodes)


def main():
    try:
        wrapper.init_script('Remote Execution')
        parser.log_args(logger)
        nodes = generate_nodes_list()

        # Check which arg was passed, cmd or script, and act accordingly..
        if getattr(args, 'cmd'):
            execute_cmd(nodes)
        else:
            execute_script(nodes)

    except KeyboardInterrupt:
        wrapper.terminate()

    except SystemExit as e:
        exit(e.code)

    except:
        logger.exception('Got exception on main handler')
        raise

    finally:
        wrapper.end_script()

if __name__ == '__main__':
    main()
