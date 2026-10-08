from __future__ import annotations

from typing import TYPE_CHECKING

from Transaction import (
    BalanceInquiryHandle,
    DepositHandle,
    TransferHandle,
    WithdarawlHandler,
)
from authentication import Authentication
from keypad import Keypad
from screen import Screen

if TYPE_CHECKING:
    from Account import Account
    from bank import Bank
    from card import Card


class AtmInterFace():

    def __init__(self, atm_id: int, location: str, bank: Bank):
        self.atm_id = atm_id
        self.location = location
        self.bank = bank
        self.screen = Screen()
        self.keypad = Keypad()
        self.authentication = Authentication(bank)

    def transction_handle(self, account: Account, answer, amount=None):
        try:
            match answer:
                case 1:
                    transaction = BalanceInquiryHandle(account)
                    transaction.transaction_handler()
                case 2:
                    transaction = WithdarawlHandler(amount, account)
                    transaction.transaction_handler()
                case 3:
                    transaction = DepositHandle(account, amount)
                    transaction.transction_handle()
                case 4:
                    print("transcation history:")
                    for transaction in account.transactions:
                        self.screen.display_message(f"Transaction ID: {transaction.transaction_id}, Type: {transaction.type}, Amount: {transaction.amount}, Timestamp: {transaction.timestamp}")
                case 5:
                    transfer = TransferHandle(amount, account)
                    transfer.transction_handelr()
                case 6:  # change_pin
                    self.authentication.change_pin_number(account)
                case _:
                    self.screen.display_message("Invalid choice. Please try again.")
        except ValueError as e:
            self.screen.display_message(f"Invalid input: {e}")

    def atm_menu(self, account: Account):
        msg = f'''
            welcome {account.coustmer.name}
            the bank u deal with is {account.bank.name}
            ------
            1: check Balance
            2:withdaraw
            3:deposit
            4:show transcation
            5:transfer_transction
            6: change pin
            7:exit
            enter your choice: '''
        exit = False

        while not exit:
            try:
                answer = int(self.keypad.get_input(msg))
            except ValueError:
                self.screen.display_message("Invalid choice. Please try again.")
                continue

            if answer == 7:
                exit = True
                self.screen.display_message("exiting...")
            else:
                try:
                    amount = float(self.keypad.get_input("enter the amount:")) if answer in [2, 3, 5] else None
                except ValueError:
                    self.screen.display_message("Invalid amount. Please try again.")
                    continue
                self.transction_handle(account, answer, amount=amount)


class CardReader():

    def __init__(self, card: Card, atm: AtmInterFace):
        self.card = card
        self.atm = atm
        self.bank = atm.bank
        self.keypad = Keypad()
        self.authentication = Authentication(self.bank)

    def insert_card(self, card: Card):
        pin = self.keypad.get_input("enter your pin number", secure=True)

        account = self.authentication.authenticate_card(pin)
        if account:
            self.atm.atm_menu(account)
        else:
            print("acsess deny")
