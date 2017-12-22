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

"""Module for useful constants"""

__all__ = [
    'REQUIRED',
    'MONEY',
    'STRING_SIZE',
    'JSON_404',
]

from django.http import JsonResponse


class ConstDict(dict):
    """
    A readonly dict.
    """

    def __readonly(self, *args, **kwargs):
        raise TypeError("Can't modify ConstDict")

    __delattr__ = __setattr__ = __setitem__ = pop = update \
        = setdefault = clear = popitem = __readonly


# Unpack in Serializer field initialization to signal the field is required
REQUIRED = ConstDict(required=True, allow_blank=False)

# Unpack in Django Model field initialization for decimal precision
MONEY = ConstDict(max_digits=19, decimal_places=10)

# Various max size for strings
STRING_SIZE = ConstDict(small=64, medium=256)

# A JSON response for generic 404 message
JSON_404 = JsonResponse({'reason': 'Not Found', 'success': False}, status=404)
