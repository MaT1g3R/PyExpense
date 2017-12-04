from datetime import datetime

from rest_framework import serializers

from expense_snek_api.core.constants import MONEY, REQUIRED, SS
from .models import Expense, Share

Serializer = serializers.Serializer


class TimedSerializerMixin:
    created_at = serializers.IntegerField()
    updated_at = serializers.IntegerField()


class IntegerList(serializers.ListField):
    child = serializers.IntegerField()


class BalanceMap(serializers.DictField):
    child = serializers.DecimalField(**MONEY)


class StringMap(serializers.DictField):
    child = serializers.CharField()


class ShareSerializer(Serializer, TimedSerializerMixin):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=SS['small'], **REQUIRED)
    description = serializers.CharField(max_length=SS['medium'], **REQUIRED)
    users = IntegerList()
    expenses = IntegerList()
    total = serializers.DecimalField(read_only=True, **MONEY)

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
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description',
                                                  instance.description)
        users = validated_data.get('users')
        if users is not None:
            instance.users.clear()
            for user in users:
                instance.users.add(user)
        instance.save()
        return instance


class UserSerializer(Serializer, TimedSerializerMixin):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=SS['small'], **REQUIRED)
    shares = IntegerList()
    expenses = IntegerList()
    balance = BalanceMap()

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
        instance.name = validated_data.get('name', instance.name)
        new_shares = validated_data.get('share')
        if new_shares is not None:
            new_shares = set(new_shares)
            old_shares = set(instance.shares)
            for to_add in new_shares - old_shares:
                to_add.users.add(instance)
                to_add.save()
            for to_del in old_shares - new_shares:
                to_del.users.remove(instance)
                to_del.save()
        instance.save()
        return instance


class ExpenseSerializer(Serializer, TimedSerializerMixin):
    id = serializers.IntegerField(read_only=True)
    description = serializers.CharField(max_length=SS['medium'], **REQUIRED)
    share = serializers.IntegerField(required=True)
    total = serializers.DecimalField(**MONEY)
    paid_by = serializers.IntegerField(required=True)
    paid_for = StringMap()
    resolved = serializers.BooleanField()

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
        paid_for = validated_data.pop('paid_for')

        if 'resolved' not in validated_data:
            validated_data['resolved'] = False

        if 'created_at' not in validated_data:
            validated_data['created_at'] = datetime.now()

        instance = Expense.objects.create(**validated_data)
        instance.generate_ratio(paid_for)
        return instance

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
        paid_for = validated_data.pop('paid_for', None)

        instance.description = validated_data.get('description',
                                                  instance.description)
        instance.share = validated_data.get('share', instance.share)
        instance.total = validated_data.get('total', instance.total)
        instance.paid_by = validated_data.get('paid_by', instance.paid_by)
        instance.save()

        if paid_for is not None:
            for ratio in instance.ratio:
                ratio.delete()
            instance.generate_ratio(paid_for)
        return instance