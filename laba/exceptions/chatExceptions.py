class NotInChat(Exception):
    def __init__(self, name, id):
        self.name = name
        self.id = id
    def __str__(self):
        return "User {0} isn't authorized to access this chat: {1}".format(self.name, self.id)

class ChatNameToLong(Exception):
    def __str__(self):
        return "The given Chat Name is to long."

class NotAdmin(Exception):
    def __str__(self):
        return "This user isn't an admin for this chat."