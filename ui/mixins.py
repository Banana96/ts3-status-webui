from django.conf import settings

from api.client import QueryClient


class TS3StatusMixin:
    def get_context_data(self, **kwargs):
        # noinspection PyUnresolvedReferences
        ctx = super().get_context_data(**kwargs)

        with QueryClient(settings.TS3_URL) as qc:
            ctx["server"] = qc.render()

        return ctx
