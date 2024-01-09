from django.db import models

# Create your models here.


class UserTerraData(models.Model):
    """
        Class is used to store data getting from terra .
    """
    fetched_data = models.JSONField(null=False, blank=False)
    user = models.CharField(max_length=50, null=False, blank=False)


class TerraUserAuth(models.Model):
    """
        Class is used to store terra authentication results.
    """
    user = models.CharField(max_length=50, null=False, blank=False)
    device = models.CharField(max_length=50, null=True, blank=False)
    terra_user_id = models.CharField(max_length=100, null=True, blank=False)
    type = models.CharField(max_length=50, null=True, blank=False)
