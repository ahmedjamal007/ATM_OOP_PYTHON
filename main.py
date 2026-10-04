from abc import ABC , abstractmethod 
from datetime import datetime
from unittest import case 

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

    def authenticate_card(self, card:Card):
        # Implement card authentication logic here
        for customer in self.customers:
            for account in customer.accounts:
                if account.linked_card == card:
                    return account

class Card():

    def __init__(self,card_number:int,pin_code:int):
        self.card_number = card_number
        self.pin_code = pin_code

    
class Atm():
    
    def __init__(self, atm_id:int, location:str, bank:Bank):
        self.atm_id = atm_id
        self.location = location
        self.bank = bank

    def atm_menu(self,account):
        msg = f'''
            welcome {account.coustmer.name}
            the bank u deal with is {account.bank.name}
            ------
            1: check Balance
            2:withdaraw
            3:transfer
            4:deposit
            5:show transcation
            '''
        print(msg)
        answer = int(input('enter your choice: '))
        if answer in range(1,5+1):
            if answer == 1:
               trans =  BalanceInquiry('b',account=account)
               trans.execute()
            if answer == 2:
                amount = float(input('enter the amount: '))
                WithdrawalTransaction(account,amount)
            if answer == 3:
                pass
            if answer == 4:
                amount = float(input('enter the amount: '))
                DepositTransaction(amount)
            if answer == 5:
                for transaction in account.transactions:
                    print(
                        transaction.type , transaction.timpestamp , transaction.id
                    )

            

                
    def insert_card(self,card:Card):
        account = self.bank.authenticate_card(card)
        if account:
            self.atm_menu(account)
        else:
            print("acsess deny")


class Transaction(ABC):

    transaction_id_counter = 0

    def __init__(self, type:str, account:Account, amount:float = None):
        self.transaction_id = self.transaction_id_counter + 1
        self.timestamp = datetime.now()
        self.type = type
        self.account = account
        self.amount = amount

    @abstractmethod
    def execute(self):
        pass


class WithdrawalTransaction(Transaction):
    def __init__(self, type:str, account:Account, amount:float):
        super().__init__(type="withdrawal", account=account, amount=amount)

    def execute(self):
        if self.account.balance >= self.amount:
            self.account.balance -= self.amount
            self.account.add_transaction(self)
            print(f"Withdrawal of {self.amount} successful. New balance: {self.account.balance}")
        else:
            print("Insufficient funds for withdrawal.")


class DepositTransaction(Transaction):
    def __init__(self, type:str, account:Account, amount:float):
        super().__init__(type="deposit", account=account, amount=amount)

    def execute(self):
        self.account.balance += self.amount
        self.account.add_transaction(self)
        print(f"Deposit of {self.amount} successful. New balance: {self.account.balance}")


class BalanceInquiry(Transaction):
    def __init__(self, type:str, account:Account):
        super().__init__(type="balance_inquiry", account=account)

    def execute(self):
        print(f"Current balance: {self.account.balance}")


bank = Bank('bank_khartum','76473sa732')
cust1 = Customer('ahmed','bahri','092412323')
account = Account('65731',2500.5,bank,cust1)
bank.add_customer(cust1)
cust1.add_account(account)
card = Card('213231','0000')
account.link_card(card)
atm = Atm(1,'bahri',bank)
atm.insert_card(card)