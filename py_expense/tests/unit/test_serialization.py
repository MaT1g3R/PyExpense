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
from itertools import chain

import pytest
from django.db.models import QuerySet
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer

from api.serializers import ExpenseSerializer, ShareSerializer, UserSerializer
from core.constants import STRING_SIZE as SS
from tests.utils import (decorators, flatten, parametrize, rand_time, random_expenses,
                         random_shares, random_users)

pytestmark = pytest.mark.django_db

name_param = parametrize('name', [None, '', '1' * (SS['small'] + 1)])
description_param = parametrize('description', [None, '', 'x' * (SS['medium'] + 1)])
created_at_param = parametrize('created_at', [None, 1])
updated_at_param = parametrize('updated_at', [None, 2])
id_param = parametrize('id', [None, 100000, -1, 's'])


def _convert_time(obj, key):
    attr = getattr(obj, key)
    try:
        ts = attr.timestamp()
    except AttributeError:
        return attr
    else:
        return int(ts)


def _convert_queryset(key, val):
    if key == 'paid_for' and isinstance(val, QuerySet):
        return {x.user.id: f'{x.numerator}/{x.denominator}' for x in val}
    if hasattr(val, 'pk'):
        return val.pk
    if isinstance(val, QuerySet):
        return [x.id for x in val]
    if hasattr(val, 'get_queryset'):
        return [x.id for x in val.get_queryset().all().distinct()]
    return val


def _assert_serialize(serializer, obj):
    obj_data = {key: _convert_time(obj, key) for key in serializer.__class__.Meta.fields}
    serializer_data = {key: _convert_queryset(key, val) for key, val in serializer.data.items()}
    obj_data = {key: _convert_queryset(key, val) for key, val in obj_data.items()}
    for key, val in obj_data.items():
        if isinstance(val, float):
            assert abs(val - serializer_data[key]) < 0.000000001
        else:
            assert val == serializer_data[key]
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
    return saved


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
@decorators(name_param, created_at_param, updated_at_param, id_param)
def test_deserialize_user_fail(name, shares, paid_by, paid_for, balance, created_at, updated_at,
                               id):
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
        random_expenses(expense_count, share=share)
    _assert_round_trip(ShareSerializer, share)


@parametrize('total', [None, 0.1, -1, ''])
@parametrize('expenses', [None, [], [1, 2], ''])
@parametrize('users', [None, [1000]])
@decorators(name_param, created_at_param, updated_at_param, id_param, description_param)
def test_deserialize_share_fail(
        name, created_at, updated_at, total, expenses, users, description, id):
    _assert_fail(random_shares, ShareSerializer, locals())


@parametrize('created_at', [True, False])
@parametrize('resolved', [True, False, None])
@parametrize('paid_for_count', [1, 10])
def test_serialize_expense(created_at, resolved, paid_for_count):
    if created_at:
        (expense,), (share,), (user,) = random_expenses(
            1, resolved=resolved, created_at=rand_time(False))
    else:
        (expense,), (share,), (user,) = random_expenses(1, resolved=resolved)
    paid_for_diff = paid_for_count - 1
    paid_for_users = random_users(paid_for_diff)
    for paid_for_u in chain(paid_for_users, [user]):
        share.users.add(paid_for_u)
        share.save()
    paid_for = {u: (1, paid_for_count) for u in chain(paid_for_users, [user])}
    expense.generate_ratio(paid_for)
    _assert_round_trip(ExpenseSerializer, expense)


@parametrize('created_at', [None, 'a'])
@parametrize('share', [None, 1000])
@parametrize('paid_by', [None, 1000])
@parametrize('resolved', [None, 's', 10])
@parametrize('paid_for', [None, 1, 'as'])
@parametrize('total', [None, -1, 'a'])
@decorators(id_param, updated_at_param, description_param)
def test_deserialize_expense_fail(id, created_at, updated_at, description,
                                  share, total, paid_by, resolved, paid_for):
    _assert_fail(random_expenses, ExpenseSerializer, locals())


@parametrize('cond', ['no_user', 'user_not_in_share', 'bad_sum', 'empty', 'bad_fraction'])
def test_deserialize_expense_fail_bad_paid_for(cond):
    share = random_shares(1)[0]
    users = random_users(5)
    user_ids = [u.id for u in users]
    share.users.add(users[0])
    share.save()
    if cond == 'no_user':
        for user in users[1:]:
            share.users.add(user)
            share.save()
        paid_for = {id_: '1/6' for id_ in chain(user_ids, '999')}
    elif cond == 'user_not_in_share':
        paid_for = {id_: '1/5' for id_ in user_ids}
    elif cond == 'bad_sum':
        paid_for = {id_: '1/4' for id_ in user_ids}
    elif cond == 'empty':
        paid_for = {}
    elif cond == 'bad_fraction':
        paid_for = {id_: '1/5/' for id_ in user_ids}
    else:
        return
    data = {'paid_for': paid_for, 'description': 'foo', 'total': 3,
            'share': share.id, 'paid_by': user_ids[0]}
    serializer = ExpenseSerializer(data=data)
    with pytest.raises(ValidationError) as e:
        serializer.is_valid(True)
    assert e.value.args[0]['paid_for']


@parametrize('cond', ['not_exist', 'not_in_share'])
def test_deserialize_expense_fail_bad_paid_by(cond):
    share = random_shares(1)[0]
    paid_for_user, paid_by_user = random_users(2)
    share.users.add(paid_for_user)
    share.save()
    if cond == 'not_exist':
        user_id = 9999
    elif cond == 'not_in_share':
        user_id = paid_by_user.id
    else:
        return

    data = {'paid_for': {str(paid_for_user.id): '1/1'}, 'description': 'foo',
            'total': 3, 'share': share.id, 'paid_by': user_id}
    serializer = ExpenseSerializer(data=data)
    with pytest.raises(ValidationError) as e:
        serializer.is_valid(True)
    assert e.value.args[0]['paid_by']
