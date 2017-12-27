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

from json import loads
from unittest.mock import MagicMock

import hypothesis.strategies as st
import pytest
from hypothesis import assume, given

from core.parse import (
    ParamSpec,
    ParseError,
    list_of_naturals,
    list_of_str,
    natural_number,
    parse_parameters,
    uri_params
)
from tests.mocks import mock_view_params
from tests.strategies import natural_list, str_list
from tests.utils import parametrize

all_specs = {
    'int': (int, '-1'),
    'natural': (natural_number, '0'),
    'natural_list': (list_of_naturals, '0,1,999,213, '),
    'str_list': (list_of_str, 'asd,asd, ,uasdgi, asd,')
}

fail_specs = {
    'int': (int, '-1.'),
    'natural': (natural_number, '-1'),
    'natural_list': (list_of_naturals, '0,1,999,213, -1'),
}


def filter_keys(func):
    for i, key in enumerate(all_specs):
        if func(i):
            yield key


key_combs = [iter(all_specs), filter_keys(lambda x: x % 2), filter_keys(lambda x: not x % 2)]

spec_list = [[ParamSpec(key, all_specs[key][0]) for key in keys] for keys in key_combs] + [[]]

param_list = [{key: all_specs[key][1] for key in keys} for keys in key_combs] + [{}]


def setup_param_fail(specs, params, fail):
    fail_key, (fail_type, fail_val) = fail
    specs = specs[:]
    params = params.copy()
    specs.append(ParamSpec(fail_key, fail_type))
    specs = list(dict.fromkeys(specs))
    params[fail_key] = fail_val
    return specs, params, fail_key, fail_type


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
    assume(not all(map(str.isdigit, lst)))
    assume(all(map(str.rstrip, lst)))
    s = ','.join(lst)
    assume(s.rstrip(', ').rstrip())
    with pytest.raises(ValueError):
        list_of_naturals(s)


@given(str_list)
def test_str_list(s):
    s = ','.join(s)
    stripped = s.rstrip(' ,').rstrip()
    if not stripped:
        assert list_of_str(s) is None
    else:
        assert list_of_str(s) == stripped.split(',')


@parametrize('specs', spec_list)
@parametrize('params', param_list)
@parametrize('add', [True, False])
def test_parse_params(specs, params, add):
    params = params.copy()
    spec_dict = {name: type_ for name, type_ in specs}
    if add:
        params['asd'] = ValueError()
    names_with_spec = {key: val for key, val in params.items() if key in spec_dict}
    assert parse_parameters(specs, params) == {
        key: spec_dict[key](val) for key, val in names_with_spec.items()
        if val is not None and spec_dict[key](val) is not None
    }


@parametrize('specs', spec_list)
@parametrize('params', param_list)
@parametrize('fail', list(fail_specs.items()))
def test_parse_params_fail(specs, params, fail):
    specs, params, fail_key, fail_type = setup_param_fail(specs, params, fail)
    with pytest.raises(ParseError) as e:
        parse_parameters(specs, params)
    expected = f"Parameter '{fail_key}' must be type '{fail_type.__name__}'"
    assert str(e.value) == expected


@parametrize('specs', spec_list)
@parametrize('params', param_list)
@parametrize('add', [True, False])
@parametrize('method', ['GET', 'POST', 'PUT', 'DELETE'])
def test_uri_params(specs, params, add, method):
    params = params.copy()
    if add:
        params['asd'] = ValueError()
    request = MagicMock()
    setattr(request, method, params)
    res = uri_params(specs, method)(mock_view_params)(request)
    assert res == parse_parameters(specs, params)


@parametrize('specs', spec_list)
@parametrize('params', param_list)
@parametrize('fail', list(fail_specs.items()))
@parametrize('method', ['GET', 'POST', 'PUT', 'DELETE'])
def test_uri_params_fail(specs, params, fail, method):
    specs, params, fail_key, fail_type = setup_param_fail(specs, params, fail)
    request = MagicMock()
    setattr(request, method, params)
    res = uri_params(specs, method)(mock_view_params)(request)
    expected = f"Parameter '{fail_key}' must be type '{fail_type.__name__}'"
    actual = loads(res.content)
    assert actual == {'success': False, 'reason': expected}
