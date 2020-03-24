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