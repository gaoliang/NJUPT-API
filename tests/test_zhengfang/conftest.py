import pytest

from njupt import Zhengfang


@pytest.fixture(scope='session')
def zhengfang():
    zhengfang = Zhengfang()
    zhengfang.account = 'account'
    zhengfang.verify = True
    return zhengfang
