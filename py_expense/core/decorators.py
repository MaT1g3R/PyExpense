__all__ = ['uri_params', 'method']

from functools import partial, wraps

from django.http import JsonResponse

from .constants import JSON_404, ParseError
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
            return JSON_404

    return wrapper
