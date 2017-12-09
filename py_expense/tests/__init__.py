from datetime import datetime
from random import choice, randint
from string import printable

from django.utils import timezone


def random_str(length):
    return ''.join(choice(printable) for _ in range(length))


def rand_strs(length, amt, unique):
    res = []
    for _ in range(amt):
        rand = random_str(length)
        if unique:
            while rand in res:
                rand = random_str(length)
        res.append(rand)
    return res


def rand_time(is_epoch):
    seconds = randint(1300000000, 1600000000)
    if is_epoch:
        return seconds
    return timezone.make_aware(datetime.fromtimestamp(seconds))
