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

import hypothesis.strategies as st
import pytest
from hypothesis import assume, given

from core.parse import ParamSpec, list_of_naturals, list_of_str, \
    natural_number, parse_parameters
from tests.strategies import natural_list, str_list

parametrize = pytest.mark.parametrize

all_specs = {
    'int': (int, '-1'),
    'natural': (natural_number, '0'),
    'natural_list': (list_of_naturals, '0,1,999,213, '),
    'str_list': (list_of_str, 'asd,asd, ,uasdgi, asd,')
}


def filter_keys(func):
    for i, key in enumerate(all_specs):
        if func(i):
            yield key


key_combs = [filter_keys(lambda x: True), filter_keys(lambda x: x % 2),
             filter_keys(lambda x: not x % 2)]


@given(st.integers())
def test_natural(i):
    int_str = str(i)
    if i < 0:
        with pytest.raises(ValueError):
            natural_number(int_str)
    else:
        assert natural_number(int_str) == i


@given(st.text())
def test_natural_fail(s: str):
    assume(not s.isdigit())
    with pytest.raises(ValueError):
        natural_number(s)


@given(natural_list)
def test_natural_list(lst):
    assume(lst)
    s = ','.join(map(str, lst))
    assert list_of_naturals(s) == lst


def test_natural_list_empty():
    assert list_of_naturals('') is None


@given(str_list)
def test_natural_list_fail(lst):
    __lst = ','.join(lst).rstrip(' ,').split(',')
    assume(not all(map(str.isdigit, __lst)))
    assume(all(map(str.rstrip, __lst)))
    with pytest.raises(ValueError):
        list_of_naturals(','.join(lst))


@given(str_list)
def test_str_list(s):
    s = ','.join(s)
    stripped = s.rstrip(' ,').rstrip()
    if not stripped:
        assert list_of_str(s) is None
    else:
        assert list_of_str(s) == stripped.split(',')


@parametrize('specs', [
    [ParamSpec(key, all_specs[key][0]) for key in keys] for keys in
    key_combs
] + [[]])
@parametrize('params', [
    {key: all_specs[key][1] for key in keys} for keys in key_combs
] + [{}])
@parametrize('add', [True, False])
def test_parse_params(specs, params, add):
    spec_dict = {name: type_ for name, type_ in specs}
    if add:
        params['asd'] = ValueError()
    names_with_spec = {key: val for key, val in params.items() if
                       key in spec_dict}
    assert parse_parameters(specs, params) == {
        key: spec_dict[key](val) for key, val in names_with_spec.items()
        if val is not None and spec_dict[key](val) is not None
    }


def test_parse_params_fail():
    pass


def test_uri_params():
    pass


def test_uri_params_fail():
    pass
