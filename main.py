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
    def transction_handle(self,account,answer,amount=None):
        try:
            match answer:
                case 1:
                    transaction = BalanceInquiryTransaction('BalanceInquiry',account)
                    transaction.execute()
                case 2:
                    transaction = WithdrawalTransaction('Withdrawal',account,amount)
                    transaction.execute()
                case 3:
                    transaction = DepositTransaction('Deposit',account,amount)
                    transaction.execute()
                case 4:
                    print("transcation history:")
                    for transaction in account.transactions:
                        print(f"Transaction ID: {transaction.transaction_id}, Type: {transaction.type}, Amount: {transaction.amount}, Timestamp: {transaction.timestamp}")
                case _:
                    print("invalid choice")
        except ValueError as e:
            print(f"Invalid input: {e}")
        
    def atm_menu(self,account):
        msg = f'''
            welcome {account.coustmer.name}
            the bank u deal with is {account.bank.name}
            ------
            1: check Balance
            2:withdaraw
            3:deposit
            4:show transcation
            5: exit
            enter your choice:
            '''
        exit = False
        
        while not exit:
            answer = int(input(msg))

            if answer == 5:
                exit = True
                print("exiting...")
            else:
                self.transction_handle(account,answer,amount=float(input("enter the amount:")) if answer in [2,3] else None)
            

        
                    

                
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


class BalanceInquiryTransaction(Transaction):
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