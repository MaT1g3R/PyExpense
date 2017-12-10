from random import uniform

import pytest
from django.utils import timezone

from api.serializers import ExpenseSerializer, ShareSerializer, UserSerializer
from tests import random_str
from tests.test_api_models import rand_time, random_shares, random_users

pytestmark = pytest.mark.django_db
parametrize = pytest.mark.parametrize


def assert_update_time(orig_update_time, instance, auto=True):
    assert instance.updated_at > orig_update_time
    if auto:
        assert instance.updated_at > instance.created_at


def assert_creation_time(instance, auto=True):
    if auto:
        assert abs(
            (instance.created_at - instance.updated_at).total_seconds()) < 2
        assert (timezone.now() - instance.created_at).total_seconds() < 5
    assert (timezone.now() - instance.updated_at).total_seconds() < 5


@parametrize('validated_data', [
    {'name': random_str(3), 'description': random_str(100)},
    {'name': random_str(8), 'description': random_str(100), 'users': 10}
])
def test_create_share(validated_data):
    serializer = ShareSerializer()
    user_count = validated_data.get('users')
    if user_count:
        validated_data['users'] = random_users(user_count)

    share = serializer.create(validated_data)

    assert_creation_time(share)
    assert share.name == validated_data['name']
    assert share.description == validated_data['description']
    if 'users' not in validated_data:
        assert not share.users.all()
    else:
        assert share.users.count() == len(validated_data['users'])
        assert set(share.users.all()) == set(validated_data['users'])
        for user in share.users.all():
            assert share in user.shares


@parametrize('orig_user_count', [0, 5, 10])
@parametrize('new_name', [True, False])
@parametrize('new_des', [True, False])
@parametrize('new_users_count', [0, 3, 5, 7])
def test_update_share(orig_user_count, new_name, new_des, new_users_count):
    serializer = ShareSerializer()
    share = random_shares(1)[0]
    updated_at = share.updated_at
    users = random_users(orig_user_count)
    for user in users:
        share.users.add(user)

    validated_data = {}
    if new_name:
        validated_data['name'] = share.name + random_str(3)
    if new_des:
        validated_data['description'] = share.description + random_str(3)
    if new_users_count is not None:
        user_diff = new_users_count - orig_user_count
    else:
        user_diff = 0
    user_out = []
    orig_user_list = list(share.users.all())
    if user_diff > 0:
        validated_data['users'] = orig_user_list + random_users(user_diff)
    elif user_diff < 0:
        validated_data['users'] = orig_user_list[:user_diff]
        user_out = orig_user_list[user_diff:]

    serializer.update(share, validated_data)
    assert_update_time(updated_at, share)

    new_name = validated_data.get('name', share.name)
    assert new_name == share.name

    new_des = validated_data.get('description', share.description)
    assert new_des == share.description

    new_users = share.users.all()
    new_users_count = new_users.count()
    assert new_users_count == new_users_count
    for user in user_out:
        assert user not in new_users
    if 'users' in validated_data:
        assert set(validated_data['users']) == set(new_users)


def test_create_user():
    serializer = UserSerializer()
    try:
        serializer.create({})
    except ValueError:
        assert True
    else:
        assert False


@parametrize('orig_share_amt', [0, 5, 10])
@parametrize('share_add_amt', [0, 3])
@parametrize('share_del_amt', [2, 5, 10])
@parametrize('update_name', [True, False])
def test_update_user(orig_share_amt, share_add_amt,
                     share_del_amt, update_name):
    if share_del_amt > orig_share_amt:
        assert True
        return
    serializer = UserSerializer()
    user = random_users(1)[0]
    orig_shares = random_shares(orig_share_amt)
    orig_time = user.updated_at
    for share in orig_shares:
        share.users.add(user)

    validated_data = {'name': user.name + random_str(2)} if update_name else {}

    if share_add_amt + share_del_amt > 0:
        added = random_shares(share_add_amt)
        new_shares = orig_shares[:-share_del_amt] + added
        deleted = orig_shares[-share_del_amt:]
        validated_data['share'] = new_shares
    else:
        deleted = []
        new_shares = list(orig_shares)

    serializer.update(user, validated_data)
    assert_update_time(orig_time, user)

    assert user.name == validated_data.get('name', user.name)
    user_shares = user.shares
    assert user_shares.count() == len(new_shares)
    assert set(user_shares) == set(new_shares)
    for deleted_share in deleted:
        assert deleted_share not in user_shares


@parametrize('user_count', [1, 5])
@parametrize('resolved', [True, False, None])
@parametrize('timed', [True, False])
def test_create_expense(user_count, resolved, timed):
    users = random_users(user_count)
    paid_for = {user: (1, len(users)) for user in users}
    validated_data = {
        'description': random_str(100),
        'share': random_shares(1)[0],
        'total': uniform(0.5, 1000.0),
        'paid_by': users[0],
        'paid_for': paid_for
    }

    if timed:
        validated_data['created_at'] = rand_time(False)
    if resolved is not None:
        validated_data['resolved'] = resolved

    serializer = ExpenseSerializer()
    expense = serializer.create(validated_data)

    if not timed:
        assert_creation_time(expense)
    if resolved is None:
        assert expense.resolved is False

    for key, val in validated_data.items():
        if key == 'paid_for':
            ratios = expense.ratio
            assert ratios.count() == user_count
            assert {ratio.user: (ratio.numerator, ratio.denominator)
                    for ratio in ratios} == paid_for
        else:
            assert getattr(expense, key) == val


def test_update_expense():
    pass
