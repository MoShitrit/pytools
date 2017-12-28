#!/usr/bin/env python
"""
This module contains the Slack class, which is responsible for the Slack integrations to scs_tools scripts.
The class is using Slack WebHooks in order to send traps, more info about it can be found in:
https://slack.com/apps/A0F7XDUAZ-incoming-webhooks
Message customization info can be found here: https://api.slack.com/docs/message-formatting
"""

import urllib
import urllib2
import socket
from print_out import print_func
from discovery import Discovery
from local_exec import LocalExec

__author__ = 'Moshe Shitrit'
__creation_date__ = '8/9/16'


class Slack:
    def __init__(self, logger, channel='#some_channel', username='some_username',
                 script_user=None, l_exec=None, discover=None, proxy=False, webhook=None):
        self.logger = logger
        self.channel = channel
        self.username = username
        if l_exec:
            self.l_exec = l_exec
        else:
            self.l_exec = LocalExec()
        if discover:
            self.discover = discover
        else:
            self.discover = Discovery(logger=self.logger, l_exec=self.l_exec)
        self.script_user = script_user
        self.no_exceptions = True
        if proxy:
            self.proxy = self.get_proxy()
            self.set_proxies()
        self.url = webhook

    def get_proxy(self):
        """
        Method to get Proxy
        :return: proxy
        """
        self.logger.info('Going to find which proxy server to use for Slack')
        # hostname = socket.gethostname()
        # Implement Proxy fetching method here
        proxy = 'foo'
        self.logger.info('Proxy server to use: {0}'.format(proxy))
        return proxy

    def set_proxies(self):
        proxies = urllib2.ProxyHandler({'http': 'http://{0}.bar:8080'.format(self.proxy),
                                        'https': 'http://{0}.bar:8080'.format(self.proxy)})
        opener = urllib2.build_opener(proxies)
        urllib2.install_opener(opener)

    def send_alert(self, message):
        """
        Using urllib, send a POST message to Slack WebHook integration.
        The request will use a Proxy server that is taken from zoom using get_proxy method.
        :param message: Message that will be sent to Slack
        """
        if self.no_exceptions:
            try:
                payload = {'payload': '{"channel": "%s", "username": "%s", "text": "%s.\n_sent from user: '
                                      '*%s@%s*_"}' % (self.channel, self.username, message,
                                                      self.script_user, socket.gethostname())}
                params = urllib.urlencode(payload)
                self.logger.info('Going to send a Slack trap with following data:\n'
                                 '\t\t\t       URL: {0}\n'
                                 '\t\t\t       Payload: {1}'.format(self.url, payload))
                r = urllib2.urlopen(self.url, params)
                self.logger.info('Response code and text from Slack: {0} {1}'.format(r.code, r.read()))

            except urllib2.URLError as e:
                print_func('Slack integration failed with error: {0}. '
                           'Make sure to update your actions in #prod-maintenance channel!'.format(e.args),
                           level='warn', logger=self.logger)
                self.no_exceptions = False
                self.logger.warning('Setting no_exceptions to False, '
                                    'which will prevent Slack integration from sending further alerts')
                self.logger.exception('Slack exception:\n{0}'.format(e))
