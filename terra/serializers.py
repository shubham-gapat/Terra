from rest_framework import serializers
from .models import (UserTerraData,
                     TerraUserAuth,
                     )


class TerraAuthSerializer(serializers.ModelSerializer):
    """
        Class is used to create, update and get serialize data for terra auth.
    """
    class Meta:
        """
            Class container containing information of the model.
        """
        model = TerraUserAuth
        fields = ['id', 'user', 'device', 'type', 'terra_user_id']


class TerraDataSerializer(serializers.ModelSerializer):
    """
        Class is used to create, update and get serialize data for terras.
    """
    class Meta:
        """
            Class container containing information of the model.
        """
        model = UserTerraData
        fields = ['id', 'user', 'fetched_data']