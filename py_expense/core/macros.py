__all__ = ['strip_trailing_commas', 'positive_integer', 'list_of_pos_ints',
           'list_of_str', 'parse_parameters']

from .constants import ParseError


def strip_trailing_commas(s):
    return s.rstrip().rstrip(',')


def positive_integer(s):
    val = int(s)
    if val < 0:
        raise ValueError
    return val


positive_integer.__name__ = 'Positive Integer'


def list_of_pos_ints(s):
    s = strip_trailing_commas(s) if s else None
    if not s:
        return None
    lst = s.split(',')
    try:
        res = [positive_integer(x) for x in lst]
    except (TypeError, ValueError):
        raise ValueError
    else:
        return res


list_of_pos_ints.__name__ = 'List of Positive Integers'


def list_of_str(s):
    s = strip_trailing_commas(s) if s else None
    return s.split(',') if s else None


list_of_str.__name__ = 'List of Strings'


def parse_parameters(param_specs, param_dict):
    res = {}
    for name, spec in param_specs.items():
        val = param_dict.get(spec.name)
        if val is None:
            continue
        try:
            val = spec.type(val)
        except (ValueError, TypeError):
            raise ParseError(
                f"Parameter '{name}' must be type '{spec.type.__name__}'"
            )
        else:
            if val is not None:
                res[name] = val
    return res
