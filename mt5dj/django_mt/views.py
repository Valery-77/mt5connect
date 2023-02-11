from rest_framework.response import Response
from rest_framework.views import APIView

from .models import InvestorModel
from .serializers import InvestorSerializer


class InvestorView(APIView):
    def get(self, request):
        existed_user = InvestorModel.objects.all()
        return Response(InvestorSerializer(existed_user, many=True).data)
