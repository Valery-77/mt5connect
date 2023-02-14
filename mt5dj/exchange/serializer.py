from rest_framework.serializers import ModelSerializer
from .models import Quotes


class QuotesSerializer(ModelSerializer):
    class Meta:
        model = Quotes
        fields = "__all__"
