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

from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer

from .models import Expense, Share, User
from .validators import validate_expense_ratio, validate_shares, validate_users

_base_fields = ('id', 'created_at', 'updated_at')


class ReadonlyMixin:
    def _read_only(self, data):
        errors = {key: 'read-only field.' for key in data
                  if key in self.Meta.read_only_fields}
        if errors:
            raise ValidationError(errors)
        return super().to_internal_value(data)


class UnixTimeStamp(serializers.IntegerField, serializers.DateTimeField):
    def to_internal_value(self, data):
        data = serializers.IntegerField.to_internal_value(self, data)
        try:
            time = datetime.fromtimestamp(data)
        except TypeError as e:
            self.fail(str(e))
        else:
            return serializers.DateTimeField.to_internal_value(self, time)

    def to_representation(self, value):
        if not value:
            return None
        return int(value.timestamp())


def update_attrs(instance, validated_data, *, key_set=None, exclude_set=None):
    for key, val in validated_data.items():
        if key_set is not None and key not in key_set:
            continue
        if exclude_set is not None and key in exclude_set:
            continue
        setattr(instance, key, val)
    instance.save()


class UserSerializer(ReadonlyMixin, ModelSerializer):
    created_at = UnixTimeStamp(read_only=True)
    updated_at = UnixTimeStamp(read_only=True)

    class Meta:
        model = User
        fields = _base_fields + ('name', 'shares', 'paid_by', 'paid_for', 'balance')
        read_only_fields = _base_fields + ('paid_by', 'paid_for', 'balance')

    def to_internal_value(self, data):
        data = data.copy()
        ret = super()._read_only(data)
        if 'shares' in data:
            ret['shares'] = validate_shares(data['shares'])
        return ret

    def create(self, validated_data):
        """
        For now, we do not allow user creation via the API.
        """
        raise ValueError("Cannot create user via API")

    def update(self, instance, validated_data):
        """
        Update an existing ``User`` instance.

        :param instance:  the ``User`` instance.

        :param validated_data:  validated client data. It can contain the 2
                                optional fields listed belw.

            name: The new name for the user.

            share: A list of ``Share`` the user is in. If this list is empty,
                   the user will no longer be in any ``Share``

        :return: The updated ``User`` instance.
        """
        new_shares = validated_data.get('shares')
        if new_shares is not None:
            new_shares = set(new_shares)
            old_shares = set(instance.shares)
            for to_add in new_shares - old_shares:
                to_add.users.add(instance)
                to_add.save()
            for to_del in old_shares - new_shares:
                to_del.users.remove(instance)
                to_del.save()
        update_attrs(instance, validated_data, key_set={'name'})
        return instance


class ShareSerializer(ReadonlyMixin, ModelSerializer):
    created_at = UnixTimeStamp(read_only=True)
    updated_at = UnixTimeStamp(read_only=True)

    class Meta:
        model = Share
        fields = _base_fields + ('name', 'description', 'users', 'expenses', 'total')
        read_only_fields = _base_fields + ('total', 'expenses')
        extra_kwargs = {'users': {'allow_empty': True}}

    def to_internal_value(self, data):
        data = data.copy()
        ret = super()._read_only(data)
        if 'users' in data:
            ret['users'] = validate_users(data['users'])
        return ret

    def create(self, validated_data):
        """
        Create a new ``Share``

        :param validated_data: the validated data from the client

        It should contain the field "name" and "description".

        It can optionally contain a field "users". It should
        be a list of user ids from the client, but in the data
        validation process it should have been transformed to a list of
        ``User`` models.

        :return: The created ``Share`` model
        """
        validated_data = validated_data.copy()
        users = validated_data.pop('users', [])
        instance = Share.objects.create(**validated_data)
        for user in users:
            instance.users.add(user)
        instance.save()
        return instance

    def update(self, instance, validated_data):
        """
        Update an existing ``Share``

        :param instance: the existing ``Share`` instance

        :param validated_data: the validated data from the client, it can
                               contain the 3 optional fields listed below.

            name: the new name.

            description: the new description.

            users: the new list of users. If this list is empty, it will
            clear all related ``User`` models from the ``Share``

        :return: The updated ``Share`` instance
        """
        users = validated_data.get('users')
        if users is not None:
            instance.users.clear()
            for user in users:
                instance.users.add(user)
        update_attrs(instance, validated_data, exclude_set={'users'})
        return instance


class ExpenseSerializer(ReadonlyMixin, ModelSerializer):
    created_at = UnixTimeStamp(required=False)
    updated_at = UnixTimeStamp(read_only=True)

    class Meta:
        model = Expense
        fields = _base_fields + ('description', 'share', 'total',
                                 'paid_by', 'paid_for', 'resolved')
        read_only_fields = ('id', 'updated_at')

    def to_internal_value(self, data):
        data = data.copy()
        errors = {}

        share_id = data.get('share')

        if share_id is not None:
            share, = validate_shares([share_id])
        else:
            share = self.fields['share']

        ratio = data.get('paid_for')
        ret = super()._read_only(data)

        if ratio is not None:
            if not ratio:
                errors['paid_for'] = 'Cannot be empty.'
            elif isinstance(ratio, dict):
                ratio_res, validate = validate_expense_ratio(ratio, share)
                if not validate:
                    errors.update(ratio_res)
                else:
                    data['paid_for'] = ratio_res
            else:
                errors['paid_for'] = 'Must be a dict.'

        paid_by = ret.get('paid_by')
        if paid_by is not None:
            if share not in paid_by.shares:
                errors['paid_by'] = f'Paid by user with ID {paid_by.id} must be in the share.'
        if errors:
            raise ValidationError(errors)
        if share_id is not None:
            ret['share'] = share
        return ret

    def to_representation(self, instance):
        res = super().to_representation(instance)
        total = res.get('total')
        if total is not None:
            res['total'] = float(total)
        ratios = res.get('paid_for')
        if ratios is not None:
            res['paid_for'] = {r.user.id: f"{r.numerator}/{r.denominator}" for r in ratios}
        return res

    def create(self, validated_data):
        """
        Create a new ``Expense``

        :param validated_data: validated client data. It contains these fields:

            description: Description of the expense

            share: The ``Share`` the expense is in

            total: The total cost of this expense

            paid_by: Which ``User`` paid for this expense

            paid_for: A mapping of ``User`` to paid ratios.

                      It should be in the form {User: (numerator, denominator)}

        It may contain two optional fields:

            created_at: The creation datetime of the expense, if not provided
                        it defaults to now.

            resolved: Wether this expense is resolved, if not
                      provided, it defaults to False

        :return: The new ``Expense`` created.
        """
        validated_data = validated_data.copy()
        paid_for = validated_data.pop('paid_for')
        return Expense.new(paid_for=paid_for, **validated_data)

    def update(self, instance, validated_data):
        """
        Update an existing ``Expense``

        :param instance: The instance to be updated.

        :param validated_data: validated client data. It may contain the
                               fields listed below.

            description: Description of the expense.

            share: The ``Share`` the expense belongs to.

            total: The total cost of this expense.

            paid_by: The ``User`` who paid for this expense.

            paid_for: A mapping of ``User`` to paid ratios.

                      It should be in the form {User: (numerator, denominator)}

            resolved: Wether this expense is resolved.

        :return: The updated expense instance.
        """
        paid_for = validated_data.get('paid_for')
        if paid_for is not None:
            instance.generate_ratio(paid_for)
        update_attrs(instance, validated_data, exclude_set={'paid_for'})
        return instance
