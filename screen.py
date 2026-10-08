import os


class Screen():

    def clear_screen(self):
        input("press any key to continue...")
        os.system('cls' if os.name == 'nt' else 'clear')

    def display_message(self, message: str):
        print(message)
        self.clear_screen()
