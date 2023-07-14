"""
    User class.
"""
from random import random

users = []


def get_current_user(id: int):
    for user in users:
        if id == user.id:
            return user
    return User()


def set_current_user(curr_user):
    for i, user in enumerate(users):
        if curr_user.id == user.id:
            users.pop(i)
            users.append(curr_user)


class User(object):
    def __init__(self):
        self.edited = False
        self.id = 0
        self.timings_repeat = [
            random.randint(720 - 50, 720 + 50),
            random.randint(1440 - 100, 1440 + 100),
            random.randint(2880 - 200, 2880 + 200),
            random.randint(4320 - 200, 4320 + 200),
            random.randint(5760 - 200, 5760 + 200),
            random.randint(7200 - 200, 7200 + 200),
            random.randint(8640 - 200, 8640 + 200)
            ]
        self.words = []
        self.words_md = []

    def set_timings(self, timings):
        self.timings_repeat = timings
        self.edited = True
