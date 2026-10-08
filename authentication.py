from __future__ import annotations

from typing import TYPE_CHECKING

from screen import Screen

if TYPE_CHECKING:
    from Account import Account
    from bank import Bank


class Authentication():

    def __init__(self, bank: Bank):
        self.bank = bank
        self.screen = Screen()

    def authenticate_card(self, pin: str):
        for account in self.bank.accounts.values():
            if account.linked_card and account.linked_card.get_pin_code() == pin:
                return account
        return None

    def change_pin_number(self, account: Account):
        self.screen.display_message("\nPassword Change press enter to countiune")
        old_pin = input("enter the old pin:")
        new_pin = input("enter the new pin:")
        new_pin_confirm = input("confirm the new pin:")
        if new_pin == new_pin_confirm and len(new_pin) > 3:
            account.linked_card.rest_pin_code(old_pin, new_pin)
            self.screen.display_message("your pin is changed...")
        else:
            self.screen.display_message("the new pin is short or the new pin and confirmation not the same try agin..")
