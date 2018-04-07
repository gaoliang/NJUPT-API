# encoding: utf-8
__author__ = 'gaoliang'


class NjuptException(Exception):
    """Base class for exceptions in this module."""

    def __init__(self, *args, **kwargs):
        super(NjuptException, self).__init__(*args, **kwargs)


class AuthenticationException(NjuptException):
    """An Authentication Exception occurred."""


class ZhengfangNotLogin(NjuptException):
    def __init__(self, message="正方账户未登录"):
        super(ZhengfangNotLogin, self).__init__(message)


class CardNotLogin(NjuptException):
    def __init__(self, message="一卡通账号未登录"):
        super(CardNotLogin, self).__init__(message)
