from rest_framework import serializers

from .models import InvestorModel


class InvestorSerializer(serializers.ModelSerializer):

    class Meta:
        model = InvestorModel
        fields = ('__all__')