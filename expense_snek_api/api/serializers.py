from rest_framework import serializers

from .models import _MONEY

Serializer = serializers.Serializer
_REQUIRED = {'required': True, 'allow_blank': False}


class TimedSerializerMixin:
    created_at = serializers.IntegerField()
    updated_at = serializers.IntegerField()


class IntegerList(serializers.ListField):
    child = serializers.IntegerField()


class BalanceMap(serializers.DictField):
    child = serializers.DecimalField(**_MONEY)


class StringMap(serializers.DictField):
    child = serializers.CharField()


class ShareSerializer(Serializer, TimedSerializerMixin):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=64, **_REQUIRED)
    description = serializers.CharField(max_length=256, **_REQUIRED)
    users = IntegerList()
    expenses = IntegerList()
    total = serializers.DecimalField(read_only=True, **_MONEY)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class UserSerializer(Serializer, TimedSerializerMixin):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=64, **_REQUIRED)
    shares = IntegerList()
    expenses = IntegerList()
    balance = BalanceMap()

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class ExpenseSerializer(Serializer, TimedSerializerMixin):
    id = serializers.IntegerField(read_only=True)
    description = serializers.CharField(max_length=256, **_REQUIRED)
    share = serializers.IntegerField(required=True)
    total = serializers.DecimalField(**_MONEY)
    paid_by = serializers.IntegerField(required=True)
    paid_for = StringMap()
    resolved = serializers.BooleanField()

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass