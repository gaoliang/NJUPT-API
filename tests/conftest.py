import os

import pytest

from njupt import Card, Zhengfang

CARD_ACCOUNT = os.environ['CARD_ACCOUNT']
CARD_RIGHT_PASSWORD = os.environ['CARD_RIGHT_PASSWORD']
CARD_WRONG_PASSWORD = "wrong_password¬"


@pytest.fixture(scope='session')
def card():
    return Card(CARD_ACCOUNT, CARD_RIGHT_PASSWORD)


ZHENGFANG_ACCOUNT = os.environ['ZHENGFANG_ACCOUNT']
ZHENGFANG_RIGHT_PASSWORD = os.environ['ZHENGFANG_RIGHT_PASSWORD']


@pytest.fixture(scope='session')
def zhengfang():
    return Zhengfang(ZHENGFANG_ACCOUNT, ZHENGFANG_RIGHT_PASSWORD)
