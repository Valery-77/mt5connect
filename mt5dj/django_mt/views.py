from rest_framework.response import Response
from rest_framework.views import APIView

from .models import InvestorModel
from .serializers import InvestorSerializer


class InvestorView(APIView):
    @staticmethod
    def get(request):
        checked = request.query_params.get('user', None)
        if checked:
            if checked == 'all':
                all_users = InvestorModel.objects.all()
                return Response(InvestorSerializer(all_users, many=True).data)
            else:
                existed_user = InvestorModel.objects.filter(email=checked)
                return Response(InvestorSerializer(existed_user, many=True).data)
        checked = request.query_params.get('id', None)
        if checked:
            try:
                existed_user = InvestorModel.objects.get(pk=checked)
                return Response(InvestorSerializer(existed_user).data)
            except:
                return Response([])
        return Response([])

    @staticmethod
    def patch(request):
        pk = request.query_params.get('id', None)
        data = request.query_params.get('data', None)
        # sr = InvestorSerializer(InvestorModel.objects.first()).data
        # sr['transaction_minus'] = 100
        # data = sr
        if pk and data:
            instance = InvestorModel.objects.get(pk=pk)
            serializer = InvestorSerializer(data=data, instance=instance)
            serializer.is_valid()
            serializer.save()
        return Response(serializer.data)

    # @staticmethod
    # def put(request, obj=None):
    #     pk = request.query_params.get('id', None)
    #     if pk:
    #         try:
    #             instance = InvestorModel.objects.get(pk=pk)
    #             print(instance)
    #         except:
    #             return Response([])
    # ser = InvestorSerializer()
    # if 'user' in request_dict and len(request_dict['user']) == 1:

    #
    # obj = InvestorModel.objects.first()
    # ser = InvestorSerializer(obj).data
    # ser['transaction_minus'] = 100
    # print(ser)
    #
    # unser = InvestorSerializer(data=ser)
    # unser.is_valid()
    # print(unser.validated_data)
    # return Response(None)
