from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING
from uuid import uuid4

from screen import Screen

if TYPE_CHECKING:
    from Account import Account


class TransactionType(Enum):
    WITHDRAWAL = "withdrawal"
    DEPOSIT = "deposit"
    TRANSFER = "transfer"
    BALANCE_INQUIRY = "balance_inquiry"
    TRANSACTION_HISTORY = "transaction_history"


class Transaction(ABC):

    def __init__(self, type: str, account: Account, amount: float = None):
        self.transaction_id = uuid4()
        self.timestamp = datetime.now()
        self.type = type
        self.account = account
        self.amount = amount

    @abstractmethod
    def execute(self):
        pass


class WithdrawalTransaction(Transaction):
    def __init__(self, type: str, account: Account, amount: float):
        super().__init__(TransactionType.WITHDRAWAL, account=account, amount=amount)

    def execute(self, call_back=False):
        self.account.balance -= self.amount
        if not call_back:
            self.account.add_transaction(self)
        return True


class DepositTransaction(Transaction):
    def __init__(self, type: str, account: Account, amount: float):
        super().__init__(TransactionType.DEPOSIT, account=account, amount=amount)

    def execute(self, call_back=False):
        self.account.balance += self.amount
        if not call_back:
            self.account.add_transaction(self)
        return f"Deposit of {self.amount} successful. New balance: {self.account.balance}"


class BalanceInquiryTransaction(Transaction):
    def __init__(self, type: str, account: Account):
        super().__init__(TransactionType.BALANCE_INQUIRY, account=account)

    def execute(self):
        return f"Current balance: {self.account.balance}"


class TransferTransaction(Transaction):
    def __init__(self, type: str, account: Account, amount: float, recipient_account: Account):
        super().__init__(TransactionType.TRANSFER, account=account, amount=amount)
        self.recipient_account = recipient_account

    def execute(self):
        Withdrawal = WithdrawalTransaction(TransactionType.WITHDRAWAL, self.account, self.amount)
        transaction_successful = Withdrawal.execute(call_back=True)
        if transaction_successful:
            Deposit = DepositTransaction(TransactionType.DEPOSIT, self.recipient_account, self.amount)
            Deposit.execute(call_back=True)
            self.account.add_transaction(self)
            self.recipient_account.add_transaction(self)
            return True
        return False


class WithdarawlHandler():
    def __init__(self, amount, account: Account):
        self.amount = amount
        self.screen = Screen()
        self.account = account

    def transaction_handler(self):
        try:
            if self.amount <= 0:
                self.screen.display_message("your balance is zero you cant witdarwal please dopsit some mony and try agin..")
            else:
                transaction = WithdrawalTransaction('withdarwal', self.account, self.amount)
                transaction.execute()
                self.screen.display_message(f"withdarwal sucess your new blance is {self.account.balance}")
        except ValueError as e:
            self.screen.display_message(e)


class BalanceInquiryHandle():
    def __init__(self, account: Account):
        self.screen = Screen()
        self.account = account

    def transaction_handler(self):
        transaction = BalanceInquiryTransaction('BalanceInquiryTransaction', self.account)
        self.screen.display_message(transaction.execute())


class DepositHandle():
    def __init__(self, account: Account, amount):
        self.screen = Screen()
        self.account = account
        self.amount = amount

    def transction_handle(self):
        transaction = DepositTransaction('Deposit', self.account, self.amount)
        sucsess = transaction.execute()
        self.screen.display_message(sucsess)


class TransferHandle():
    def __init__(self, amount: float, account: Account):
        self.recipient_account_number = input("enter the recipient_account number:.. ")
        self.screen = Screen()
        self.amount = amount
        self.account = account

    def transction_handelr(self):
        recipient_account = self.account.bank.get_account_by_number(self.recipient_account_number)
        if recipient_account is None:
            self.screen.display_message("Recipient account not found.")
            return
        confirmation = input(
            f"Are you sure you want to transfer {self.amount} to {recipient_account.coustmer.name} "
            f"(Account Number: {recipient_account.account_number})? (yes/no): "
        )
        if confirmation.lower() != 'yes':
            self.screen.display_message("Transfer cancelled.")
            return
        transaction = TransferTransaction('Transfer', self.account, self.amount, recipient_account)
        sucsess = transaction.execute()
        if sucsess == True:
            self.screen.display_message("transfer sucsess")
