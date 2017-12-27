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

from api.models import User
from api.serializers import UserSerializer
from core.constants import STRING_SIZE as SS
from tests.utils import parametrize, random_expenses, random_shares, random_users

pytestmark = pytest.mark.django_db


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
    assert serializer_data == obj_data
    return serializer_data


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
    serializer = UserSerializer(user)
    serializer_data = _assert_serialize(serializer, user)
    content = JSONRenderer().render(serializer_data)
    stream = BytesIO(content)
    data = JSONParser().parse(stream)
    new_serializer = UserSerializer(user, data=data)
    assert new_serializer.is_valid(True)
    saved = new_serializer.save()
    assert saved == User.objects.get(pk=saved.id)


@parametrize('name', [None, '', '1' * (SS['small'] + 1)])
@parametrize('share', [None, [99]])
def test_deserialize_user_fail(name, share):
    if name is None and share is None:
        return
    user = random_users(1)[0]
    data = {'name': name} if name is not None else {}
    if share is not None:
        data['shares'] = share
    serializer = UserSerializer(user, data=data, partial=True)
    assert not serializer.is_valid()
