from datetime import datetime

from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.generic import TemplateView

from ui.mixins import TS3StatusMixin


@method_decorator(cache_page(settings.TS3_STATUS_CACHE_TIME), name="get")
class IndexView(TS3StatusMixin, TemplateView):
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["public_addr"] = settings.TS3_PUBLIC_ADDR
        ctx["fetch_time"] = datetime.now().strftime("%Y-%d-%m %H:%M:%S")
        return ctx
