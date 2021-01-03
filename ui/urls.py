from django.urls import path

from ui.views import *

urlpatterns = [path("", IndexView.as_view())]
