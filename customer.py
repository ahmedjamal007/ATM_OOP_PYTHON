from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from Account import Account


class Customer():

    def __init__(self, name, address, phone_number):
        self.name = name
        self.address = address
        self.phone_number = phone_number
        self.accounts = {}

    def add_account(self, account: Account):
        self.accounts[account.account_number] = account
