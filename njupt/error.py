# encoding: utf-8
__author__ = 'Gao Liang'


class NjuptError(Exception):
    def __init__(self, *args, **kwargs):
        super(NjuptError, self).__init__(*args, **kwargs)
