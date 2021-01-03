from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from api.client import QueryClient, datetime


class StatusViewSet(ViewSet):
    @method_decorator(cache_page(settings.TS3_STATUS_CACHE_TIME))
    def list(self, *args, **kwargs):
        with QueryClient(settings.TS3_URL) as qc:
            response = qc.render()

        return Response({
            **response,
            "fetch_time": datetime.now().strftime("%Y-%d-%m %H:%M:%S")
        })
