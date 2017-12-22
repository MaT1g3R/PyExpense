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

"""Module containing useful decorators."""

__all__ = [
    'method',
]

from functools import partial, wraps
from typing import Iterable, Union

from django.http import JsonResponse


def method(func=None, *, allowed: Union[str, Iterable[str]]):
    """
    Decorate a view function to only allow certain methods.
    :param func: The function to decorate.
    :param allowed: The allowed method(s).
    """
    if not func:
        return partial(method, allowed=allowed)

    if isinstance(allowed, str):
        allowed = {allowed}

    @wraps(func)
    def wrapper(request):
        if request.method in allowed:
            return func(request)
        else:
            allowed_lst = ', '.join(f"'{x}'" for x in allowed)
            reason = (
                f"Method '{request.method}' is not allowed. "
                f"Allowed methods: {allowed_lst}"
            )
            return JsonResponse(
                {'success': False, 'reason': reason}, status=404
            )

    return wrapper
