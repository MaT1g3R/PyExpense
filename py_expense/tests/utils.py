#  PyExpense, Django powered webapp to track shared expenses.
#  Copyright (C) 2017 Peijun Ma
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as
#  published by the Free Software Foundation, either version 3 of the
#  License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

from datetime import datetime
from functools import wraps
from random import choice, randint, uniform
from string import printable

import pytest
from django.utils import timezone

from api.models import Expense, Share, User

parametrize = pytest.mark.parametrize


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


def random_expenses(amt, *, share=None, created_at=None, resolved=None) -> tuple:
    shares = random_shares(amt)
    users = random_users(amt)
    res = []
    for i in range(amt):
        kwargs = dict(
            created_at=created_at, description=random_str(123),
            share=share or shares[i], paid_by=users[i], total=uniform(0.5, 1000.0),
            paid_for={users[i]: (1, 1)}, resolved=resolved
        )
        if created_at is None:
            del kwargs['created_at']
        if resolved is None:
            del kwargs['resolved']
        res.append(Expense.new(**kwargs))
    return res, shares, users


def flatten(it):
    if isinstance(it, str):
        yield it
    else:
        try:
            it = (x for x in it)
        except TypeError:
            yield it
        else:
            yield from (flatten(x) for x in it)


def decorators(*dec_list):
    def decorate(func):
        for dec in dec_list:
            func = dec(func)

        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

    return decorate
