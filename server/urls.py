from django.urls import path, include

urlpatterns = [
    path("", include("ui.urls")),
    path("api/", include("api.urls")),
]
