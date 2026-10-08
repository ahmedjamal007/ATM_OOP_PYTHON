from Account import Account
from atm import AtmInterFace, CardReader
from bank import Bank
from card import Card
from customer import Customer


def open_account(bank: Bank, customer: Customer, account_number: int, balance: float, pin: str):
    """Create an account for a customer, link a card to it and register it at the bank."""
    account = Account(account_number, balance, bank, customer)
    account.link_card(Card(account_number, pin))
    customer.add_account(account)
    bank.add_customer(customer)
    return account


def build_bank():
    bank = Bank("MyBank", "SWIFT123")

    john = Customer("John Doe", "123 Main St", "555-1234")
    open_account(bank, john, 1001, 5000.0, "1234")

    # a second account so transfers (menu option 5) have somewhere to go
    jane = Customer("Jane Roe", "456 Oak Ave", "555-5678")
    open_account(bank, jane, 1002, 1200.0, "4321")

    return bank


def main():
    bank = build_bank()
    atm = AtmInterFace(1, "Main Street", bank)

    card = bank.get_account_by_number(1001).linked_card
    card_reader = CardReader(card, atm)
    card_reader.insert_card(card)


if __name__ == "__main__":
    main()
