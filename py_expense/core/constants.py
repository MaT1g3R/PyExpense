"""
Module for useful constants
"""
__all__ = [
    'REQUIRED', 'MONEY', 'STRING_SIZE', 'SS', 'JSON_404', 'ParamSpec',
    'ParseError',
]

from typing import NamedTuple

from django.http import JsonResponse


class ConstDict(dict):

    def __readonly(self, *args, **kwargs):
        raise TypeError("Can't modify ConstDict")

    __delattr__ = __setattr__ = __setitem__ = pop = update \
        = setdefault = clear = popitem = __readonly


class ParseError(ValueError):
    pass


REQUIRED = ConstDict(required=True, allow_blank=False)
MONEY = ConstDict(max_digits=19, decimal_places=10)
SS = STRING_SIZE = ConstDict(small=64, medium=256)
JSON_404 = JsonResponse({'reason': 'Not Found', 'success': False}, status=404)
ParamSpec = NamedTuple('ParamSpec', [('name', str), ('type', callable)])
