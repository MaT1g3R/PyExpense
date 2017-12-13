from datetime import datetime
from random import choice, randint, uniform
from string import printable

from django.utils import timezone

from api.models import Expense, Share, User


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


def random_shares(amt):
    return [Share.objects.create(name=n, description=d) for n, d in
            zip(rand_strs(12, amt, True), rand_strs(123, amt, False))]


def random_users(amt):
    return [User.objects.create(name=n) for n in rand_strs(12, amt, True)]


def random_expenses(amt) -> tuple:
    shares = random_shares(amt)
    users = random_users(amt)
    return [Expense.objects.create(
        created_at=rand_time(False), description=random_str(123),
        share=shares[i], paid_by=users[i], total=uniform(0.5, 1000.0)
    ) for i in range(amt)], shares, users
