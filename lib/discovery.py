#!/usr/bin/env python
"""
This module contains all the discovery methods I'm using in my scripts..
"""

from local_exec import LocalExec

__author__ = 'Moshe Shitrit'
__creation_date__ = '1/5/16'


class Discovery:

    def __init__(self, args=None, logger=None, l_exec=None):
        self.logger = logger
        self.args = args
        if l_exec:
            self.l_exec = l_exec
        else:
            self.l_exec = LocalExec()


    @staticmethod
    def dict_to_string(dic, key_to_ignore=None):
        st = ''
        for key in dic.keys():
            if key == key_to_ignore:
                pass
            else:
                st += '{0}={1},'.format(key, dic[key])
        return st.rstrip(',')


