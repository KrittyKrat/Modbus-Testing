class Register:
    def __init__(self, address, number, represent, verify) -> None:
        self.address = address
        self.number = number
        self.represent = represent
        self.verify = verify
        self.gotten = ""
        self.expected = ""
        self.success = ""