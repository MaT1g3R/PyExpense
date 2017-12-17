# Create your views here.

from django.http import JsonResponse

from api.models import Share
from api.serializers import ShareSerializer
from core import ParamSpec, list_of_pos_ints, list_of_str, method, uri_params


@method(allowed='GET')
@uri_params(
    spec={'name__in': ParamSpec('name', list_of_str),
          'id__in': ParamSpec('id', list_of_pos_ints)},
    method='GET'
)
def share_list(request, *, params):
    shares = Share.objects.filter(**params) if params else Share.objects.all()
    serializer = ShareSerializer(shares, many=True)
    return JsonResponse(serializer.data, safe=False)


@method(allowed='POST')
def update_share(request):
    pass
