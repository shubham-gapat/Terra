import json
import os

from rest_framework.generics import (
    CreateAPIView,
     RetrieveAPIView
)
from rest_framework import status
from rest_framework.response import Response
import requests
from .serializers import (TerraAuthSerializer, TerraDataSerializer)
from .models import (UserTerraData, TerraUserAuth)


class ResponseInfo(object):
    """
    Class for setting how API should send response.
    """

    def __init__(self, **args):
        self.response = {
            "status_code": args.get('status', 200),
            "error": args.get('error', None),
            "data": args.get('data', []),
            "message": [args.get('message', 'Success')]
        }


class ConnectTerra(RetrieveAPIView):
    """
    API View to connect with terra api and get connection data
    """
    authentication_classes = ()
    permission_classes = ()
    serializer_class = TerraAuthSerializer

    def __init__(self, **kwargs):
        """
        Constructor for creating response format
        """
        self.response_format = ResponseInfo().response
        super(ConnectTerra, self).__init__(**kwargs)

    def post(self, request, *args, **kwargs):
        """
        Post method to connect with terra api and get connection data.
        """
        url =  os.getenv("TERRA_CONNECT_API_URL")
        payload = {
            "reference_id": request.data['reference_id'],
            "providers": request.data['device_type'],
            "language": "en"
        }
        headers = {
            "accept": "application/json",
            "dev-id": os.getenv("TERRA_DEV_ID"),
            "content-type": "application/json",
            "x-api-key": os.getenv("TERRA_API_KEY")
        }
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        url = response.json()["url"]
        user_status = self.get_serializer(data={"user": request.data['reference_id'],
                                                "device": request.data['device_type'],
                                                "type": request.data["type"]})
        if user_status.is_valid(raise_exception=True):
            user_status.save()
        self.response_format["data"] = {"terra_connect_url": url}
        self.response_format["message"] = "Terra connect url created"
        self.response_format["status_code"] = status.HTTP_200_OK
        return Response(self.response_format)


class GetTerraData(CreateAPIView):
    """
    API View to get data from terra and store data
    """
    authentication_classes = ()
    permission_classes = ()
    serializer_class = TerraDataSerializer
    queryset = UserTerraData.objects.all()

    def __init__(self, **kwargs):
        """
        Constructor for creating response format
        """
        self.response_format = ResponseInfo().response
        super(GetTerraData, self).__init__(**kwargs)

    def post(self, request, *args, **kwargs):
        """
        Post method to store data getting from terra.
        """
        user_data = request.body
        user_json = json.loads(user_data.decode('utf-8'))
        if 'user' in user_json.keys() or 'new_user' in user_json.keys():
            terraData = TerraDataSerializer(data={"fetched_data": user_json,
                                                  "user":  user_json['new_user']['reference_id'] if user_json['type'] == "user_reauth" else
                            user_json['user']['reference_id']})
            if terraData.is_valid(raise_exception=True):
                terraData.save()
            if (user_json['type'] == "user_reauth" and user_json['status'] == "success") or (
                    user_json['type'] == "auth" and user_json['status'] == "success"):
                terra_auth_user = TerraUserAuth.objects.filter(
                    user=user_json['user']['reference_id'])
                for terra_user in terra_auth_user:
                    if terra_user.terra_user_id == (
                            user_json['new_user']['user_id'] if user_json['type'] == "user_reauth" else
                            user_json['user']['user_id']):
                        continue
                    else:
                        terra_user.terra_user_id = user_json['new_user']['user_id'] \
                            if user_json['type'] == "user_reauth" else user_json['user']['user_id']
                        terra_user.save()
            if user_json['type'] == "deauth":
                terra_auth_user = TerraUserAuth.objects.filter(user=user_json['new_user']['reference_id'] if user_json['type'] == "user_reauth" else
                            user_json['user']['reference_id'])
                terra_data = UserTerraData.objects.filter(user=user_json['new_user']['reference_id'] if user_json['type'] == "user_reauth" else
                            user_json['user']['reference_id'])
                for user in terra_auth_user:
                    user.delete()
                for terra in terra_data:
                    terra.delete()
            self.response_format["data"] = None
            self.response_format["status_code"] = status.HTTP_200_OK
            self.response_format["message"] = "Terra data created"
        return Response(self.response_format)


class DisconnectTerraApiView(RetrieveAPIView):
    """
        API View to disconnect from terra
    """
    authentication_classes = ()
    permission_classes = ()
    serializer_class = TerraAuthSerializer

    def __init__(self, **kwargs):
        """
        Constructor for creating response format
        """
        self.response_format = ResponseInfo().response
        super(DisconnectTerraApiView, self).__init__(**kwargs)

    def get_queryset(self):
        """
        Method for getting terra auth queryset.
        """
        if getattr(self, 'swagger_fake_view', False):
            return TerraUserAuth.objects.none()
        return TerraUserAuth.objects.filter(user=self.kwargs["pk"]).first()

    def get(self, request, *args, **kwargs):
        """
        Get method to get status of terra authentication.
        """
        try:
            terra_user = self.get_queryset()
            url = os.getenv("TERRA_DISCONNECT_API_URL") + "?user_id=" + str(terra_user.terra_user_id)
            headers = {
                "accept": "application/json",
                "dev-id": os.getenv("TERRA_DEV_ID"),
                "x-api-key": os.getenv("TERRA_API_KEY")
            }
            response = requests.delete(url, headers=headers)
            terra_auth_user = TerraUserAuth.objects.filter(terra_user_id=terra_user.terra_user_id,
                                                           device=terra_user.device)
            for user in terra_auth_user:
                user.delete()
            self.response_format["status_code"] = status.HTTP_200_OK
            self.response_format["data"] = None
            self.response_format["error"] = None
            self.response_format["message"] = "Terra user is deactivated successfully."
        except TerraUserAuth.DoesNotExist:
            self.response_format["data"] = None
            self.response_format["error"] = "user"
            self.response_format["status_code"] = status.HTTP_400_BAD_REQUEST
            self.response_format["message"] = "Terra authentication status Failed"
        return Response(self.response_format)

