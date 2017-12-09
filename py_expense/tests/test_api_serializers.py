import pytest
from django.utils import timezone

from api.serializers import ShareSerializer
from tests import random_str
from tests.test_api_models import random_shares, random_users

pytestmark = pytest.mark.django_db
parametrize = pytest.mark.parametrize


def update_data(instance, data, fields, fieldname, mutation: callable):
    if fields.get(fieldname):
        data[fieldname] = mutation(getattr(instance, fieldname))


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

    assert share.name == validated_data['name']
    assert share.description == validated_data['description']
    assert abs((share.created_at - share.updated_at).total_seconds()) < 2
    assert (timezone.now() - share.created_at).total_seconds() < 5
    if 'users' not in validated_data:
        assert not share.users.all()
    else:
        assert share.users.count() == len(validated_data['users'])
        assert set(share.users.all()) == set(validated_data['users'])
        for user in share.users.all():
            assert share in user.shares


@parametrize('orig_user_count,update_fields', [
    (0, {'name': True, 'description': True}),
    (5, {'name': True, 'description': True}),
    (3, {'name': True, 'users': 4}),
    (7, {'description': True, 'users': 2}),
    (10, {'name': True, 'description': True, 'users': 0}),
])
def test_update_share(orig_user_count, update_fields):
    serializer = ShareSerializer()
    share = random_shares(1)[0]
    updated_at = share.updated_at
    users = random_users(orig_user_count)
    for user in users:
        share.users.add(user)
    final_user_count = update_fields.pop('users', orig_user_count)
    validated_data = {}
    for field in update_fields:
        update_data(
            share, validated_data, update_fields,
            field, lambda x: x + random_str(3)
        )
    user_diff = final_user_count - orig_user_count
    user_out = []
    orig_user_list = list(share.users.all())
    if user_diff > 0:
        validated_data['users'] = orig_user_list + random_users(user_diff)
    elif user_diff < 0:
        validated_data['users'] = orig_user_list[:user_diff]
        user_out = orig_user_list[user_diff:]

    serializer.update(share, validated_data)
    assert share.updated_at > updated_at

    new_name = validated_data.get('name', share.name)
    assert new_name == share.name

    new_des = validated_data.get('description', share.description)
    assert new_des == share.description

    new_users = share.users.all()
    new_users_count = new_users.count()
    assert final_user_count == new_users_count
    for user in user_out:
        assert user not in new_users
    if 'users' in validated_data:
        assert set(validated_data['users']) == set(new_users)


def test_update_user():
    pass


def test_create_expense():
    pass


def test_update_expense():
    pass
