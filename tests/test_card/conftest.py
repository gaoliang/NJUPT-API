import pytest

from njupt import Card


@pytest.fixture(scope='session')
def card():
    card = Card()
    card.account = 'account'
    card.verify = True
    return card
