users = []


class User:
    def __init__(self, std_id, name, address, email):
        self.id = std_id
        self.email = email
        self.name = name
        self.address = address
        users.append(self)

    def get_name_cap(self):
        return self.name.capitalize()
