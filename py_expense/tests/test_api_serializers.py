import pytest
from django.utils import timezone

from api.serializers import ShareSerializer
from tests import random_str
from tests.test_api_models import random_users

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize('validated_data', [
    {'name': random_str(3), 'description': random_str(100)},
    {'name': random_str(8), 'description': random_str(100), 'users': 10}
])
def test_create_share(validated_data):
    serializer = ShareSerializer()
    user_count = validated_data.get('users')
    if user_count:
        validated_data['users'] = random_users(user_count)

    orig_data = dict(validated_data)
    share = serializer.create(validated_data)

    assert share.name == orig_data['name']
    assert share.description == orig_data['description']
    assert abs((share.created_at - share.updated_at).total_seconds()) < 2
    assert (timezone.now() - share.created_at).total_seconds() < 5
    if 'users' not in orig_data:
        assert not share.users.all()
    else:
        assert share.users.count() == len(orig_data['users'])
        assert set(share.users.all()) == set(orig_data['users'])
        for user in share.users.all():
            assert share in user.shares


def test_update_share():
    pass


def test_update_user():
    pass


def test_create_expense():
    pass


def test_update_expense():
    pass
