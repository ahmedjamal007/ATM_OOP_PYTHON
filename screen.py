import os

from keypad import Keypad


class Screen():

    def __init__(self):
        self.keypad = Keypad()

    def clear_screen(self):
        self.keypad.get_input("press any key to continue...")
        os.system('cls' if os.name == 'nt' else 'clear')

    def display_message(self, message: str):
        print(message)
        self.clear_screen()
