# Create your views here.
from functools import partial, wraps

from django.http import JsonResponse

from api.models import Share
from api.serializers import ShareSerializer


def function_name(func=None, *, name):
    if not func:
        return partial(function_name, name=name)
    func.__name__ = name

    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper


@function_name(name='Positive Integer')
def positive_integer(s):
    val = int(s)
    if val < 0:
        raise ValueError
    return val


def parse_parameters(param_specs, param_dict):
    res = {}
    for name, type_ in param_specs.items():
        val = param_dict.get(name)
        print(val)
        if val is None:
            continue
        try:
            val = type_(val)
        except (ValueError, TypeError):
            raise ValueError(
                f"Parameter '{name}' must be type '{type_.__name__}'"
            )
        else:
            res[name] = val
    return res


def share_list(request):
    if request.method != 'GET':
        return JsonResponse({}, status=404)
    try:
        params = parse_parameters({'name': str, 'id': positive_integer},
                                  request.GET)
    except ValueError as e:
        return JsonResponse(
            {'success': False, 'reason': e.args[0]}, status=400
        )
    shares = Share.objects.filter(**params) if params else Share.objects.all()
    serializer = ShareSerializer(shares, many=True)
    return JsonResponse(serializer.data, safe=False)
