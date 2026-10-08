import getpass


class Keypad():
    """The ATM keypad: the only place in the program that reads what the user types.

    Use get_input() everywhere. Pass secure=True for anything that must not be
    echoed to the screen (PINs), and it is routed to get_secure_input().
    """

    def get_input(self, prompt: str, secure: bool = False):
        if secure:
            return self.get_secure_input(prompt)
        return input(prompt)

    def get_secure_input(self, prompt: str):
        return getpass.getpass(prompt)
