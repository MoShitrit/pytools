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
parser.add_argument('--cmd', help='The command to run on remote nodes',
                    required=True)
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


def iterate_nodes_and_call_exec_func(r_exec, nodes):
    """
    Get the r_exec object and the list of nodes as arguments.
    Create an additional list called "work" which will append the amount of nodes
    equal to the provided batch argument. If batch_sleep argument was provided,
    it will sleep x seconds between each batch.
    """
    work = list()
    count = 0
    for node in nodes:
        count += 1
        work.append(node)
        if len(work) == int(args.batch):
            r_exec.exec_func_threading(nodes=work, command=args.cmd)
            count = 0
            if args.batch_sleep > 0 and count < (len(nodes) - len(work)):
                logger.info('*** Sleeping for %d seconds before moving on to next batch ***',
                            args.batch_sleep)
                sleep.sleep_func(args.batch_sleep)
            work = list()
    if len(work) > 0:
        r_exec.exec_func_threading(nodes=work, command=args.cmd)


def main():
    try:
        wrapper.init_script('Remote Execution')
        parser.log_args(logger)
        nodes = generate_nodes_list()
        if confirm('run {0} command on multiple servers'.format(args.cmd), wrapper=wrapper,
                   title='running {0} command'.format(args.cmd)):
            r_exec = RemoteExec(args=args, wrapper=wrapper)
            iterate_nodes_and_call_exec_func(r_exec, nodes)

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
