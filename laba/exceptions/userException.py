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

class UserNotInitialized(Exception):
    def __str__(self):
        return "User hasn't been initialized yet or has been logged out."

class NotInitializeable(Exception):
    def __init__(self, name):
        self.name = name
    def __str__(self):
        return "Class {0} can't be initialized direct. Please create subclass and overide constructor".format(self.name)

class SessionNotStarted(Exception):
    def __str__(self):
        return "Session hasn't been started yet."

class RegistrationErrorInfoMissing(Exception):
    def __init__(self, vals):
        self.vals = vals
    def __str__(self):
        #return "Missing Information: {0}".format(", ".join(self.vals))
        return "Missing Information: {0}".format(self.vals)

class RegistrationErrorDupplicate(Exception):
    def __init__(self, obj):
        self.obj = obj
    def __str__(self):
        return "{0} already in use".format(self.obj)

class InvalidToken(Exception):
    def __init__(self, token):
        self.token = token
    def __str__(self):
        return "Invalid Token provided: {0}".format(self.token)
