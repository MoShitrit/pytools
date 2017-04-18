#!/usr/bin/env python
"""
This module contains all the methods which to prompt the user for inputs
"""

from color import Color

__author__ = 'Moshe Shitrit'
__creation_date__ = '1/5/16'


def confirm(prompt, title, wrapper):
    """
    Prompts for confirmation from the user before performing an execution command.
    The function gets as arguments: The question to prompt, the title of the action for logging
    and the logger configuration. The function will also log the question and the response from the user.
    If yes- it will return true,
    """
    try:
        wrapper.logger.info('Going to prompt user for confirmation before {0}..'.format(title))
        while True:
            ans = raw_input('\n{0}{1}{2}WARNING! You are about to {3}!{4} Are you sure? (y/n): '.
                            format(Color.BOLD, Color.UNDERLINE, Color.RED, str.upper(prompt), Color.END))
            if ans not in ['y', 'Y', 'n', 'N']:
                print 'ERROR: Invalid input. Please enter y or n..'
                continue
            elif ans in ['y', 'Y']:
                wrapper.logger.info('User confirmed, proceeding..')
                return True
            elif ans in ['n', 'N']:
                wrapper.logger.warning('User declined..')
                return False

    except KeyboardInterrupt:
        wrapper.terminate()


def confirm_no_log(prompt):
    """
    Prompts the user with a question provided as an arguments.
    Gets [Y,y,N,n] as answers, returns True for 'y', False for 'n'.
    """
    try:
        while True:
            ans = raw_input(prompt)
            if ans not in ['y', 'Y', 'n', 'N']:
                print 'ERROR: Invalid input. Please enter y or n..'
                continue
            elif ans in ['y', 'Y']:
                return True
            elif ans in ['n', 'N']:
                return False

    except KeyboardInterrupt:
        exit(1)


def choose_from_list(list_to_choose, wrapper):
    """
    Gets a list as an argument, prompts the user to choose the desired item and return the selection..
    """
    try:
        for item in list_to_choose:
            print '[{0}]  {1}'.format(list_to_choose.index(item), item)
        selection = int(raw_input('\nPlease enter your choice and press [ENTER]: '))
        return selection
    except KeyboardInterrupt:
        wrapper.terminate()

