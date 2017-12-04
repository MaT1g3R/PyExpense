from rest_framework import serializers

from expense_snek_api.core.constants import MONEY, REQUIRED, SS
from .models import Share

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

        :param validated_data:
        :return:
        """
        pass

    def update(self, instance, validated_data):
        pass