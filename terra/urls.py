from django.urls import path
from .views import (ConnectTerra, GetTerraData, DisconnectTerraApiView)

urlpatterns = [
    path('getTerraConnectUrl/', ConnectTerra.as_view(), name='get-terra-connect-url'),
    path("getterradata/", GetTerraData.as_view(), name="get-terra-data"),
    path("disconnectTerraStatus/<int:pk>/", DisconnectTerraApiView.as_view(), name="disconnect-terra"),
]
