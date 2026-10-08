from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import uuid4

if TYPE_CHECKING:
    from Transaction import Transaction
    from bank import Bank
    from card import Card
    from customer import Customer


class Account():

    def __init__(self, account_number: int, balance: float, bank: Bank, coustmer: Customer):
        self.transactions_number = uuid4()
        self.transactions = []
        self.bank = bank
        self.account_number = account_number
        self.balance = balance
        self.linked_card = None
        self.coustmer = coustmer

    def add_transaction(self, transaction: Transaction):
        self.transactions.append(transaction)

    def link_card(self, card: Card):
        self.linked_card = card
