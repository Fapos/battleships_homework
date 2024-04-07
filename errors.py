from typing import Optional

class BattleShipsCallError(Exception):
    def __init__(self, value: str):
        self.value = value

    def __str__(self):
        return self.value


class BattleShipsOutRangeError(Exception):
    def __init__(self, value: Optional[str] = None):
        self.value = value

    def __str__(self):
        if self.value:
            return self.value
        else:
            return 'Value out of range'


class BattleShipsInvalidValueError(Exception):
    def __init__(self, value: Optional[str] = None):
        self.value = value

    def __str__(self):
        if self.value:
            return self.value
        else:
            return 'Value is invalid'


class BattleShipsCellIsBusyError(Exception):
    def __init__(self, value: Optional[str] = None):
        self.value = value

    def __str__(self):
        if self.value:
            return self.value
        else:
            return 'Cell is busy'


class BattleShipsMaxShipsOnBoardError(Exception):
    def __init__(self, value: Optional[str] = None):
        self.value = value

    def __str__(self):
        if self.value:
            return self.value
        else:
            return 'Max ships on board'


class BattleShipsAlreadyShotError(Exception):
    def __init__(self, value: Optional[str] = None):
        self.value = value

    def __str__(self):
        if self.value:
            return self.value
        else:
            return 'Cell already shot'
