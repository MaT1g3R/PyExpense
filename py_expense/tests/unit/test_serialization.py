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

"""
Tests for (de)serialization behaviour

Model creation/uptade is tested in ``test_serializers_create_update``, so
we will only be testing data validation for (de)serialization.
"""

from io import BytesIO

import pytest
from django.db.models import QuerySet
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer

from api.serializers import ShareSerializer, UserSerializer
from core.constants import STRING_SIZE as SS
from tests.utils import decorators, flatten, parametrize, random_expenses, random_shares, \
    random_users

pytestmark = pytest.mark.django_db

name_param = parametrize('name', [None, '', '1' * (SS['small'] + 1)])
created_at_param = parametrize('created_at', [None, 1])
updated_at_param = parametrize('updated_at', [None, 2])


def _convert_time(obj, key):
    attr = getattr(obj, key)
    try:
        ts = attr.timestamp()
    except AttributeError:
        return attr
    else:
        return int(ts)


def _convert_queryset(val):
    if isinstance(val, QuerySet):
        return [x.id for x in val]
    return val


def _assert_serialize(serializer, obj):
    obj_data = {key: _convert_time(obj, key) for key in serializer.__class__.Meta.fields}
    serializer_data = {key: _convert_queryset(val) for key, val in serializer.data.items()}
    obj_data = {key: _convert_queryset(val) for key, val in obj_data.items()}
    for key, val in serializer_data.items():
        obj_val = obj_data[key]
        assert val == obj_val or val == [x.id for x in obj_val.get_queryset().all().distinct()]
    return serializer_data


def _assert_round_trip(SerializerCls, obj):
    serializer = SerializerCls(obj)
    serializer_data = _assert_serialize(serializer, obj)
    content = JSONRenderer().render(serializer_data)
    stream = BytesIO(content)
    data = {key: val for key, val in JSONParser().parse(stream).items()
            if key not in serializer.Meta.read_only_fields}
    new_serializer = SerializerCls(obj, data=data)
    assert new_serializer.is_valid(True)
    saved = new_serializer.save()
    assert saved == obj.__class__.objects.get(pk=saved.id)


def _assert_fail(random_func, Serializer, kwargs):
    data = {key: val for key, val in kwargs.items() if val is not None}
    obj = next(flatten(random_func(1)))
    serializer = Serializer(obj, data=data, partial=True)
    valid = serializer.is_valid()
    assert not valid or (valid and not data)


@parametrize('paid_by_count', [0, 1, 10])
@parametrize('paid_for_count', [0, 1, 10])
@parametrize('share_count', [0, 1, 10])
def test_serialize_user(paid_by_count, paid_for_count, share_count):
    user = random_users(1)[0]
    if share_count:
        shares = random_shares(share_count)
        for share in shares:
            share.users.add(user)
            share.save()
    max_expense_count = max(paid_by_count, paid_for_count)
    if max_expense_count:
        expenses, *_ = random_expenses(max_expense_count)
        for i, exp in enumerate(expenses):
            if i < paid_by_count:
                exp.paid_by = user
                exp.save()
            if i < paid_for_count:
                exp.generate_ratio({user: (1, 1)})
    _assert_round_trip(UserSerializer, user)


@parametrize('shares', [None, [1000]])
@parametrize('paid_by', [None, [], [1, 2, 3]])
@parametrize('paid_for', [None, [], [1, 3, 4]])
@parametrize('balance', [None, {}, {"3": 1.0}])
@decorators(name_param, created_at_param, updated_at_param)
def test_deserialize_user_fail(name, shares, paid_by, paid_for, balance, created_at, updated_at):
    _assert_fail(random_users, UserSerializer, locals())


@parametrize('user_count', [0, 1, 10])
@parametrize('expense_count', [0, 1, 10])
def test_serialize_share(user_count, expense_count):
    share = random_shares(1)[0]
    if user_count:
        users = random_users(user_count)
        for user in users:
            share.users.add(user)
            share.save()
    if expense_count:
        random_expenses(expense_count, share)
    _assert_round_trip(ShareSerializer, share)


@parametrize('total', [None, 0.1, -1, ''])
@parametrize('expenses', [None, [], [1, 2], ''])
@parametrize('users', [None, [1000]])
@parametrize('description', [None, '', 'x' * (SS['medium'] + 1)])
@decorators(name_param, created_at_param, updated_at_param)
def test_deserialize_share_fail(name, created_at, updated_at, total, expenses, users, description):
    _assert_fail(random_shares, ShareSerializer, locals())
