from abc import ABC , abstractmethod 
from datetime import datetime
from uuid import uuid4
from enum import Enum
import os
class TransactionType(Enum):
    WITHDRAWAL = "withdrawal"
    DEPOSIT = "deposit"
    TRANSFER = "transfer"
    BALANCE_INQUIRY = "balance_inquiry"
    TRANSACTION_HISTORY = "transaction_history"

class Customer():
    def __init__(self, name, address, phone_number):

        self.name = name
        self.address = address
        self.phone_number = phone_number
        self.accounts = []

    def add_account(self, account):
        self.accounts.append(account)

class Account():
    transactions_number = 0
    def __init__(self, account_number:int, balance: float, bank: Bank,coustmer:Customer):
        self.transactions_number += 1
        self.transactions = []
        self.bank = bank
        self.account_number = account_number
        self.balance = balance
        self.linked_card = None
        self.coustmer = coustmer

    def add_transaction(self, transaction:Transaction):
        self.transactions.append(transaction)


    def link_card(self, card:Card):
        self.linked_card = card

    
class Bank():

    def __init__(self,name,swift_code):
        self.name = name
        self.swift_code = swift_code
        self.customers = []

    def add_customer(self, customer:Customer):
        self.customers.append(customer)

    def authenticate_card(self, pin:str):
        # Implement card authentication logic here
        for customer in self.customers:
            for account in customer.accounts:
                if account.linked_card.pin_code == pin:
                    return account
                raise ValueError("Invalid PIN. Access denied.")
    def get_account_by_number(self, number:str):
        for customer in self.customers:
            for account in customer.accounts:
                if account.account_number == number:
                    return account
        raise ValueError("Account not found.")

class Card():

    def __init__(self,card_number:int,pin_code:int):
        self.card_number = card_number
        self.pin_code = pin_code


class CardReader():

    def __init__(self,card:Card,atm:Atm):
        self.card = card
        self.atm = atm

    def insert_card(self,card:Card):
        pin = input("enter your pin number")

        account = self.atm.bank.authenticate_card(pin)
        if account:
            self.atm.atm_menu(account)
        else:
            print("acsess deny")

class Screen():
    
    def display_message(self,message:str):
        print(message)


    def clear_screen(self):
        confirmation = input("press any key to continue...")
        os.system('cls' if os.name == 'nt' else 'clear')




class Atm():
    
    def __init__(self, atm_id:int, location:str, bank:Bank):
        self.atm_id = atm_id
        self.location = location
        self.bank = bank
        self.screen = Screen()
    def transction_handle(self,account,answer,amount=None):
        try:
            match answer:
                case 1:
                    transaction = BalanceInquiryTransaction('BalanceInquiry',account)
                    transaction.execute()
                    
                    self.screen.clear_screen()
                case 2:
                    transaction = WithdrawalTransaction('Withdrawal',account,amount)
                    transaction.execute()
                    self.screen.clear_screen()
                case 3:
                    transaction = DepositTransaction('Deposit',account,amount)
                    transaction.execute()
                    self.screen.clear_screen()
                case 4:
                    print("transcation history:")
                    for transaction in account.transactions:
                        self.screen.display_message(f"Transaction ID: {transaction.transaction_id}, Type: {transaction.type}, Amount: {transaction.amount}, Timestamp: {transaction.timestamp}")
                        self.screen.clear_screen()
                case 5:
                    recipient_account_number = input("Enter the recipient account number: ")
                    recipient_account = self.bank.get_account_by_number(recipient_account_number)
                    if recipient_account is None:
                        self.screen.display_message("Recipient account not found.")
                    else:
                        # show msg to confirm the transfer with the recipient's name and account number
                        confirmation = input(f"Are you sure you want to transfer {amount} to {recipient_account.coustmer.name} (Account Number: {recipient_account.account_number})? (yes/no): ")
                        if confirmation.lower() != 'yes':
                            self.screen.display_message("Transfer cancelled.")
                            return
                        transaction = TransferTransaction('Transfer',account,amount,recipient_account=recipient_account)
                        transaction.execute()
                        self.screen.clear_screen()
                case _:
                    self.screen.display_message("Invalid choice. Please try again.")
                    self.screen.clear_screen()
        except ValueError as e:
            self.screen.display_message(f"Invalid input: {e}")
            self.screen.clear_screen()

    def atm_menu(self,account):
        msg = f'''
            welcome {account.coustmer.name}
            the bank u deal with is {account.bank.name}
            ------
            1: check Balance
            2:withdaraw
            3:deposit
            4:show transcation
            5:transfer_transction
            6: exit
            enter your choice: '''
        exit = False
        
        while not exit:
            answer = int(input(msg))
            if answer == 6:
                exit = True
                self.screen.display_message("exiting...")
            else:
                self.transction_handle(account,answer,amount=float(input("enter the amount:")) if answer in [2,3,5] else None)
            



class Transaction(ABC):

    def __init__(self, type:str, account:Account, amount:float = None):
        self.transaction_id = uuid4()
        self.timestamp = datetime.now()
        self.type = type
        self.account = account
        self.amount = amount

    @abstractmethod
    def execute(self):
        pass


class WithdrawalTransaction(Transaction):
    def __init__(self, type:str, account:Account, amount:float):
        super().__init__(TransactionType.WITHDRAWAL, account=account, amount=amount)

    def execute(self,call_back = False ):
        self.account.balance -= self.amount
        if call_back:
            pass
        else:
            self.account.add_transaction(self)
            return True

        return False


class DepositTransaction(Transaction):
    def __init__(self, type:str, account:Account, amount:float):
        super().__init__(TransactionType.DEPOSIT, account=account, amount=amount)

    def execute(self,call_back = False ):
        self.account.balance += self.amount
        if call_back:
            pass
        else:
            self.account.add_transaction(self)
        self.screen.display_message(f"Deposit of {self.amount} successful. New balance: {self.account.balance}")


class BalanceInquiryTransaction(Transaction):
    def __init__(self, type:str, account:Account):
        super().__init__(TransactionType.BALANCE_INQUIRY, account=account)

    def execute(self):
        print(f"Current balance: {self.account.balance}")



class TransferTransaction(Transaction):
    def __init__(self, type:str, account:Account, amount:float, recipient_account:Account):
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

bank = Bank('bank_khartum','76473sa732')
cust1 = Customer('ahmed','bahri','092412323')
cust2 = Customer('ali','bahri','092412323')
account = Account('65731',2500.5,bank,cust1)
account2 = Account('65732',2500.5,bank,cust1)
cust2.add_account(account2)
account2.link_card(Card('213232','0000'))
bank.add_customer(cust1)
cust1.add_account(account)
card = Card('213231','0000')
account.link_card(card)
atm = Atm(1,'bahri',bank)
c = CardReader(card,atm)
c.insert_card(card)