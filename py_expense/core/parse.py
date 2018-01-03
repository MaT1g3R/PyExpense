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

"""Module for URI parameter parsing"""

__all__ = [
    'uri_params',
    'natural_number',
    'pos_int',
    'list_of_naturals',
    'list_of_str',
    'ParamSpec',
]

from functools import wraps
from typing import Any, Callable, Dict, Iterable, List, NamedTuple, Optional

from django.http import JsonResponse

from .decorators import func_name


class ParseError(ValueError):
    """
    Error raised by ``parse_parameters`` to signal an error in parsing
    """
    pass


class ParamSpec(NamedTuple):
    name: str
    type: Callable


@func_name('Natural Number')
def natural_number(s: str) -> int:
    """
    Try to convert a string to a natural numnber (n >= 0)

    :param s: the string to convert.
    :return: the converted natural number.
    :raises ValueError: If the conversion failed.
    """
    if not isinstance(s, int) and not s.isdigit():
        raise ValueError('Fail.')
    val = int(s)
    if val < 0:
        raise ValueError('Cannot be negative.')
    return val


@func_name('Positive Integer')
def pos_int(s: str) -> int:
    """
    Try to convert a string to a positive integer (n >= 1)

    :param s: the string to convert.
    :return: the converted natural number.
    :raises ValueError: If the conversion failed.
    """
    val = natural_number(s)
    if val == 0:
        raise ValueError('Must be positive.')
    return val


@func_name('List of Natural Numbers')
def list_of_naturals(s: str) -> Optional[List[int]]:
    """
    Try to convert a comma seprated string to a list of natural numbers.
    :param s: The comma seprated string.
    :return: A list of natural numbers.
    :raises ValueError: If the conversion failed.
    """

    s = s.rstrip(' ,').rstrip()
    if not s:
        return None
    lst = s.split(',')
    try:
        res = [natural_number(x) for x in lst]
    except (TypeError, ValueError) as e:
        raise ValueError(str(e))
    else:
        return res


@func_name('List of Strings')
def list_of_str(s: str) -> Optional[List[str]]:
    """
    Try to split a comma seprated string into a list.
    :param s: The string to be split.
    :return: The split list.
    """
    s = s.rstrip(' ,').rstrip()
    return s.split(',') if s else None


def parse_parameters(param_specs: Iterable[ParamSpec],
                     param_dict: Dict[str, str]) -> Dict[str, Any]:
    """
    Parse a requst URI parameters into Python types based on the specs.

    :param param_specs: The specs for conversion.
    :param param_dict: The URI parameters.
    :return: The parsed URI parameters.
    :raises ParseError: If the parsing failed.
    """
    res = {}
    for name, type_ in param_specs:
        val = param_dict.get(name)
        if val is None:
            continue
        try:
            val = type_(val)
        except (ValueError, TypeError):
            raise ParseError(
                f"Parameter '{name}' must be type '{type_.__name__}'"
            )
        else:
            if val is not None:
                res[name] = val
    return res


def uri_params(spec: Iterable[ParamSpec], method: str):
    """
    Decorate a view function to parse URI parameters.

    This will inject an argument with name ``params`` into the view function.

    :param spec: The URI parameter spec.
    :param method: The method name to get the request parameters from.
    """

    def decorate(func):

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

    return decorate
