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

"""Validators for serializers"""

from rest_framework.exceptions import ValidationError

from api.models import Expense, Share, User
from core.parse import natural_number


def __validate_id_list(ModelCls, name, value):
    """
    value -> list of models

    :param ModelCls: The model class.
    :param value: The value to be validated.
    :return: A list of models.
    :raises ValidationError: If validation failed.
    """
    if len(value) == 0:
        return []

    try:
        id_set = set(map(natural_number, value))
    except (TypeError, ValueError) as e:
        raise ValidationError({type(e).__name__: str(e)})

    found = ModelCls.objects.filter(pk__in=id_set)

    if found.count() != len(id_set):
        diff = id_set - set(f.id for f in found)
        diff_repr = ', '.join(map(str, diff))
        raise ValidationError({name: f"{ModelCls.__name__} with IDs '{diff_repr}' not found."})
    return list(found)


def validate_users(value):
    """value -> list of users"""
    return __validate_id_list(User, 'users', value)


def validate_expenses(value):
    """value -> list of expenses"""
    return __validate_id_list(Expense, 'expenses', value)


def validate_shares(value):
    """value -> list of shares"""
    return __validate_id_list(Share, 'shares', value)
