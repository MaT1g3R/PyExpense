import pytest

from api.models import User, Share

pytestmark = pytest.mark.django_db


def test_user_shares_none():
    user = User.objects.create(name='foo')
    share = Share.objects.create(name='bar', description='baz')
    assert not user.shares


def test_expense_ratios():
    pass


def test_expense_generate_ratios():
    pass
