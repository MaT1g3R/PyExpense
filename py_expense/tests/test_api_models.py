import pytest

from api.models import Share, User
from tests import rand_strs

pytestmark = pytest.mark.django_db
new_user = User.objects.create
new_share = Share.objects.create


def random_shares(amt):
    return [new_share(name=n, description=d) for n, d in
            zip(rand_strs(12, amt, True), rand_strs(123, amt, False))]


def random_users(amt):
    return [new_user(name=n) for n in rand_strs(12, amt, True)]


def test_user_shares_none():
    user, *_ = random_users(1)
    new_share(name='bar', description='baz')
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


def test_expense_ratios():
    pass


def test_expense_generate_ratios():
    pass
