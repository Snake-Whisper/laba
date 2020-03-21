class BadUserCredentials(Exception):
    def __init__(self, user):
        self.user = user
    def __str__(self):
        return "User {0} doesn't provide correct login credentials or doesn't exist.".format(self.user)

class UserDisabled(Exception):
    def __init__(self, user):
        self.user = user
    def __str__(self):
        return "User {0} isn't enabled.".format(self.user)
