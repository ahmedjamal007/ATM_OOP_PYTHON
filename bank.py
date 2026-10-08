from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from Account import Account
    from customer import Customer


class Bank():

    def __init__(self, name, swift_code):
        self.name = name
        self.swift_code = swift_code
        self.accounts = {}

    def add_account(self, account: Account):
        self.accounts[str(account.account_number)] = account

    def add_customer(self, customer: Customer):
        for account in customer.accounts.values():
            self.add_account(account)

    def get_account_by_number(self, number):
        return self.accounts.get(str(number))
