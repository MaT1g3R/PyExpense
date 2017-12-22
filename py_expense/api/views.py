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

from django.http import JsonResponse

from api.models import Share
from api.serializers import ShareSerializer
from core import ParamSpec, list_of_naturals, list_of_str, method, uri_params


@method(allowed='GET')
@uri_params(
    spec=(ParamSpec('name', list_of_str), ParamSpec('id', list_of_naturals)),
    method='GET'
)
def share_list(request, *, params):
    """
    /api/v1/shares/list

    Method: GET

    Get a list of shares based on the provided names/IDs.
    Returns all shares if neither names nor IDs are provided.

    The request is evaluated at an AND basis, so if both name and id are
    provided, any share with name in the list AND id in the list are returned.

    URI parameters:
        Optional:
            name: a comma separated list of share names.
            id: a comma separated list of share ids.

    Response Body: A list of shares. Each share contains these fields:
        id: ID of the share
        type: int

        name: Name of the share
        type: str

        created_at: Unix epoch of the creation time of the share.
        type: int

        updated_at: Unix epoch of the latest updated time of the share.
        type: int

        description: Description of the share
        type: str

        users: List of IDs of users in the share.
        type: List[int]

        expenses: List of IDs of expenses in the share.
        type: List[int]

        total: The total cost for all expenses in the share.
        type: float
    """
    if params:
        params = {f'{key}__in': val for key, val in params.items()}
        shares = Share.objects.filter(**params).distinct()
    else:
        shares = Share.objects.all().distinct()
    serializer = ShareSerializer(shares, many=True)
    return JsonResponse(serializer.data, safe=False)


@method(allowed='POST')
def share_create(request):
    """
    /api/v1/shares/create

    Method: POST

    Create a new share.

    Request Body:
        Required:
            name: Name of the share. Max length 64 characters.
            type: str

            description: Description of the share. Max length 256 characters.
            type: str

        Optional:
            users: List of IDs of users in this share.
            type: List[int]

    Response Body:
        success: True is the creation was successful, otherwise False.
        type: bool

        reason: Failure reason, if any.
        type: str

        id: ID of the created share.
        type: int

        created_at: Unix epoch of the share creation time.
        type: int
    """
    pass
