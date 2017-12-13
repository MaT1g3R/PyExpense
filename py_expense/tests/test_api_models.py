import pytest

from api.models import ExpenseRatio, Share
from .utils import random_expenses, random_shares, random_users

pytestmark = pytest.mark.django_db


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
