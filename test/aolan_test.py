import requests

from njupt.models.account import AolanAccount, JwxtAccount

account = AolanAccount()
print(account.login(account='B15080517', password="dwdw"))
