#!/usr/bin/env python

""" A test script to send a Slack through my WebHook """

from lib.slack import Slack
from lib.wrappers import Wrapper
from lib.logger_config import MyLogger
import logging

__author__ = 'Moshe Shitrit <moshe1750@gmail.com>'
__creation_date__ = '12/15/17'

# Build the logger
my_log = MyLogger(__file__, level=logging.DEBUG)
logger = my_log.get_logger()

# Build the script wrapper
wrapper = Wrapper(logger, my_log.log_file)

# ================== END GLOBAL ================== #


def main():
    wrapper.init_script('Slack messaging')
    s = Slack(logger=logger,
              username='<sender name>',
              webhook='https://hooks.slack.com/<mySpecialHook>',
              channel='#channel_to_post_to')
    s.send_alert('This is a test message')
    wrapper.end_script()


if __name__ == '__main__':
    main()
