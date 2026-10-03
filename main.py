from abc import ABC , abstractmethod 
from datetime import datetime 

class Customer():
    def __init__(self, name, address, phone_number,account:Account):

        self.name = name
        self.address = address
        self.phone_number = phone_number
        self.account = account


class Account():
    transactions_number = 0
    def __init__(self, account_number:int, balance: float, bank: Bank, linked_card: list):
        self.transactions_number += 1
        self.transactions = []
        self.bank = bank
        self.account_number = account_number
        self.balance = balance
        self.linked_card = linked_card

    def add_transaction(self, transaction:Transaction):
        self.transactions.append(transaction)
class Bank():

    def __init__(self,name,swift_code,customers:Customer):
        self.name = name
        self.swift_code = swift_code
        self.customers = customers

class Card():

    def __init__(self,card_number:int,pin_code:int,expiry_date:datetime,account:Account):
        self.card_number = card_number
        self.pin_code = pin_code
        self.expiry_date = expiry_date
        self.account = account

class Atm():
    
    def __init__(self, atm_id:int, location:str, bank:Bank):
        self.atm_id = atm_id
        self.location = location
        self.bank = bank


class Transaction(ABC):


    def __init__(self, transaction_id:int, timestamp:datetime, type:str, account:Account,amount:float = None):
        self.transaction_id = transaction_id
        self.timestamp = timestamp
        self.type = type
        self.account = account
        self.amount = amount

    @abstractmethod
    def execute(self):
        pass


class Withdrawal(Transaction):
    def __init__(self, transaction_id:int, timestamp:datetime, date:datetime, account:Account, amount:float):
        super().__init__(type="withdrawal",amount=amount, transaction_id=transaction_id, timestamp=timestamp, account=account)


    def execute(self):
        if self.account.balance >= self.amount:
            self.account.balance -= self.amount
            self.account.add_transaction(self)
            print(f"Withdrawal of {self.amount} successful. New balance: {self.account.balance}")
        else:
            print("Insufficient funds for withdrawal.")

    

    
account1 = Account(account_number=123456, balance=1000.0, bank=None, linked_card=[])
customer1 = Customer(name="John Doe", address="123 Main St", phone_number="555-1234", account=account1)
transaction1 = Withdrawal(transaction_id=1, timestamp=datetime.now(), date=datetime.now(), account=account1, amount=200.0)
transaction1.execute()  # This will perform the withdrawal and print the result