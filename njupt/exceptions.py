# encoding: utf-8
__author__ = 'gaoliang'


class NjuptException(Exception):
    """Base class for exceptions in this module."""

    def __init__(self, *args, **kwargs):
        super(NjuptException, self).__init__(*args, **kwargs)


class AuthenticationException(NjuptException):
    """An Authentication Exception occurred."""


class UnauthorizedError(NjuptException):
    """Not authorized Error"""


class TemporaryBannedException(NjuptException):
    """Temporary Banned by Server"""
