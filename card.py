class Card():

    def __init__(self, card_number: int, pin_code: str):
        self.card_number = card_number
        self.__pin_code = pin_code

    def get_pin_code(self):
        return self.__pin_code

    def rest_pin_code(self, old_pin, new_pin):
        if self.__pin_code == old_pin:
            self.__pin_code = new_pin
            return True
        return False
