from abc import ABC , abstractmethod 
from datetime import datetime
from uuid import uuid4
from enum import Enum
import os
from pymupdf import message
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
        self.accounts = {}

    def add_account(self, account):
        self.accounts[account.account_number] = account

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

class authentication():
    
    def __init__(self, bank:Bank):
        self.bank = bank

    def authenticate_card(self, pin:str):
        for account in self.bank.accounts.values():
            if account.linked_card and account.linked_card.get_pin_code() == pin:
                return account
        return None
    
class Bank():

    def __init__(self,name,swift_code):
        self.name = name
        self.swift_code = swift_code
        self.accounts = {}

    def add_customer(self, customer:Customer):
        for account in customer.accounts.values():
            self.accounts[account.account_number] = account

    def get_account_by_number(self, number:str):
        return self.accounts.get(number)

class Card():

    def __init__(self,card_number:int,pin_code:int):
        self.card_number = card_number
        self.__pin_code = pin_code

    def get_pin_code(self):
        return self.__pin_code
        

    def rest_pin_code(self,old_pin, new_pin):
        if self.__pin_code == old_pin:
            self.__pin_code = new_pin
            return True
        return False


class CardReader():

    def __init__(self,card:Card,atm:Atm):
        self.card = card
        self.atm = atm
        self.authentication = authentication(atm.bank)

    def insert_card(self,card:Card):
        pin = input("enter your pin number")

        account = self.authentication.authenticate_card(pin)
        if account:
            self.atm.atm_menu(account)
        else:
            print("acsess deny")

class Screen():
    
    def clear_screen(self):
        confirmation = input("press any key to continue...")
        os.system('cls' if os.name == 'nt' else 'clear')

    def display_message(self,message:str):
            print(message)
            self.clear_screen()



class WithdarawlHandler():
    def __init__(self , amount,account:Account):
        self.amount = amount
        self.screen = Screen()
        self.account = account


    def transaction_handler(self):
        try:
            if self.amount <= 0:
                self.screen.display_message("your balance is zero you cant witdarwal please dopsit some mony and try agin..")
            else:
                transaction = WithdrawalTransaction('withdarwal',self.account,self.amount)
                transaction.execute()
                self.screen.display_message(f"withdarwal sucess your new blance is {self.account.balance}")
        except ValueError as e:
            self.screen.display_message(e)

class BalanceInquiryHandle():
    def __init__(self,account):
        self.screen = Screen()
        self.account = account 

    def transaction_handler(self):
        transaction = BalanceInquiryTransaction('BalanceInquiryTransaction',self.account)
        self.screen.display_message(transaction.execute())

    

class DepositHandle():
    def __init__(self,account,amount):
        self.screen = Screen()
        self.account = account
        self.amount = amount

    def transction_handle(self):
        transaction = DepositTransaction('Deposit',self.account,self.amount)
        sucsess = transaction.execute()
        self.screen.display_message(sucsess)





class TransferHandle():
    pass


class Atm():
    
    def __init__(self, atm_id:int, location:str, bank:Bank):
        self.atm_id = atm_id
        self.location = location
        self.bank = bank
        self.screen = Screen()
    def transction_handle(self,account:Account,answer,amount=None):
        try:
            match answer:
                case 1:
                    transaction = BalanceInquiryHandle(account)
                    transaction.transaction_handler()
                case 2:
                    transaction = WithdarawlHandler(amount,account)
                    transaction.transaction_handler()
                case 3:
                    transaction = DepositHandle(account,amount)
                    transaction.transction_handle()
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
                case 6: #change_pin
                    self.screen.display_message("\nPassword Change press enter to countiune")
                    old_pin = input("enter the old pin:")
                    new_pin = input("enter the new pin:")
                    new_pin_confirm = input("confirm the new pin:")
                    if new_pin == new_pin_confirm and len(new_pin) > 3:
                        card = account.linked_card.rest_pin_code(old_pin,new_pin)
                    else:
                        self.screen.display_message("the new pin is short or the new pin and confirmation not the same try agin..")
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
            6: change pin
            7:exit
            enter your choice: '''
        exit = False
        
        while not exit:
            answer = int(input(msg))
            if answer == 7:
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
        return f"Deposit of {self.amount} successful. New balance: {self.account.balance}"


class BalanceInquiryTransaction(Transaction):
    def __init__(self, type:str, account:Account):
        super().__init__(TransactionType.BALANCE_INQUIRY, account=account)

    def execute(self):
        return f"Current balance: {self.account.balance}"



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

bank = Bank("MyBank", "SWIFT123")
c = Customer("John Doe", "123 Main St", "555-1234")
account1 = Account(1001, 5000.0, bank,c)
c.add_account(account1)
case = Card(1234567890, "1234")
account1.link_card(case)
atm = Atm(1, "Main Street", bank)
bank.add_customer(c)
card_reader = CardReader(case, atm)
card_reader.insert_card(case)
