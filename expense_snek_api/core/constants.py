"""
Module for useful constants
"""

__all__ = ['REQUIRED', 'MONEY', 'STRING_SIZE', 'SS']


class ConstDict(dict):

    def __readonly(self, *args, **kwargs):
        raise TypeError("Can't modify ConstDict")

    __delattr__ = __setattr__ = __setitem__ = pop = update \
        = setdefault = clear = popitem = __readonly


REQUIRED = ConstDict(required=True, allow_blank=False)
MONEY = ConstDict(max_digits=19, decimal_places=10)
STRING_SIZE = ConstDict(small=64, medium=256)

SS = STRING_SIZE