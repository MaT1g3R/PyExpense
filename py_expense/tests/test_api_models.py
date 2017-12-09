from random import uniform

import pytest

from api.models import Expense, ExpenseRatio, Share, User
from tests import rand_strs, rand_time, random_str

pytestmark = pytest.mark.django_db


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


def test_user_shares_none():
    user, *_ = random_users(1)
    Share.objects.create(name='bar', description='baz')
    assert not user.shares


def test_user_shares():
    user, *_ = random_users(1)
    shares_in = random_shares(3)[:2]
    for share in shares_in:
        share.users.add(user)
        share.save()
    assert user.shares.count() == len(shares_in)
    assert set(user.shares) == set(shares_in)


def test_user_shares_duplicate():
    share, *_ = random_shares(1)
    user, *_ = random_users(1)
    id_ = share.id

    share.users.add(user)
    share.save()

    share_get_new = Share.objects.get(id=id_)
    share_get_new.users.add(user)

    assert user.shares.count() == 1
    assert set(user.shares) == {share}


def test_expense_ratios_none():
    (expense, *_), _, _ = random_expenses(1)
    assert not expense.ratio


def test_expense_ratios():
    (expense, *_), shares, users = random_expenses(5)
    paid_for = {user: (1, 5) for user in users}
    expense.generate_ratio(paid_for)
    ratios = list(expense.ratio)

    for ratio in ratios:
        assert ratio.expense == expense

    actual_paid_for = {ratio.user: (ratio.numerator, ratio.denominator) for
                       ratio in ratios}
    assert paid_for == actual_paid_for


def test_expense_delete():
    (expense, *_), shares, users = random_expenses(5)
    paid_for = {user: (1, 5) for user in users}
    expense.generate_ratio(paid_for)
    id_ = expense.id
    assert ExpenseRatio.objects.filter(expense=id_).count() == 5
    expense.delete()
    assert not ExpenseRatio.objects.filter(expense=id_)
