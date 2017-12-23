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

from copy import deepcopy
from json import loads
from random import randint

import hypothesis.strategies as st
from django.http import HttpRequest
from hypothesis import given

from core import func_name, method
from tests.utils import random_str

non_empty_str = st.text(min_size=1)
non_empty_str_iter = st.iterables(non_empty_str)


def _mock_view(request):
    return request


def _assert_method(method_, allowed):
    request = HttpRequest()
    request.method = method_
    wrapped = method(_mock_view, allowed=allowed)
    res = wrapped(request)
    assert res == _mock_view(request)


def _assert_method_fail(wrong_method, allowed):
    request = HttpRequest()
    request.method = wrong_method
    wrapped = method(_mock_view, allowed=allowed)
    res = wrapped(request)
    assert res.status_code == 404
    json = loads(res.content)
    assert json['success'] is False
    assert 'is not allowed. ' in json['reason']


@given(non_empty_str)
def test_method_single(allowed):
    _assert_method(allowed, allowed)


@given(non_empty_str)
def test_method_single_fail(allowed):
    while True:
        wrong_method = random_str(randint(1, 100))
        if wrong_method != allowed:
            break
    _assert_method_fail(wrong_method, allowed)


@given(non_empty_str_iter)
def test_method_multiple(it):
    for m in deepcopy(it):
        _assert_method(m, deepcopy(it))


@given(non_empty_str_iter)
def test_method_multiple_fail(it):
    set_ = set(deepcopy(it))
    while True:
        wrong_method = random_str(randint(1, 100))
        if wrong_method not in set_:
            break
    _assert_method_fail(wrong_method, it)


@given(non_empty_str)
def test_func_name(name):
    wrapped = func_name(name)(_mock_view)
    req = HttpRequest()
    assert wrapped.__name__ == _mock_view.__name__ == name
    assert _mock_view(req) == wrapped(req)
