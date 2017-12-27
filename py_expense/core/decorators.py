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
    'func_name',
]

from functools import wraps
from typing import Callable, Iterable, Union

from django.http import JsonResponse


def method(allowed: Union[str, Iterable[str]]):
    """
    Decorate a view function to only allow certain methods.
    :param func: The function to decorate.
    :param allowed: The allowed method(s).
    """

    if isinstance(allowed, str):
        allowed = {allowed}

    def decorate(func):

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
                return JsonResponse({'success': False, 'reason': reason}, status=404)

        return wrapper

    return decorate


def func_name(name: str):
    """
    Change the function __name__ attribute
    :param name: The name to change to.
    """

    def decorate(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        wrapper.__name__ = name
        return wrapper

    return decorate
