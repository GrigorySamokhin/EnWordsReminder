"""
    User class.
"""

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
        self.timings_repeat = [60, 180, 360, 720, 1240, 2480, 4520]
        self.words = []
        self.words_md = []

    def set_timings(self, timings):
        self.timings_repeat = timings
        self.edited = True
