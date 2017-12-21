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

__all__ = ['uri_params', 'method']

from functools import partial, wraps

from django.http import JsonResponse

from .constants import ParseError
from .macros import parse_parameters


def uri_params(func=None, *, spec, method):
    if not func:
        return partial(uri_params, spec=spec, method=method)

    @wraps(func)
    def wrapper(request):
        try:
            params = parse_parameters(spec, getattr(request, method))
        except ParseError as e:
            return JsonResponse(
                {'success': False, 'reason': e.args[0]}, status=400
            )
        else:
            return func(request, params=params)

    return wrapper


def method(func=None, *, allowed):
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
