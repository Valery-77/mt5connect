import json

import requests as requests
from django.http import HttpResponse
from rest_framework import generics
from rest_framework.decorators import api_view

from .models import Quotes
from .serializer import QuotesSerializer


@api_view(('GET', 'POST'))
def index(request):
    if request.method == 'GET':
        try:
            url = 'http://localhost:8000/api/demo_mt5/list'
            response = requests.get(url).json()[0]
            api_key_expired = response.get('api_key_expired')
            no_exchange_connection = response.get('no_exchange_connection')
            if api_key_expired == "true":
                commentary = 'Ключ APi истек'
                payload = json.dumps({"commentary": commentary})
            elif no_exchange_connection == 'true':
                commentary = 'Нет связи с биржей'
                payload = json.dumps({"commentary": commentary})
            elif api_key_expired == "true" and no_exchange_connection == 'true':
                commentary = 'Нет связи с биржей и ключ APi истек'
                payload = json.dumps({"commentary": commentary})
            else:
                commentary = 'на редкость все хорошо'
                payload = json.dumps({"commentary": commentary})
            headers = {'Content-Type': 'application/json'}
            patch_url = 'http://127.0.0.1:8000/api/demo_mt5/update/1/'
            requests.request("PATCH", patch_url, headers=headers, data=payload)
            return HttpResponse("SUCCESSFUL PATCH")
        except Exception as e:
            return HttpResponse(e)


class QuotesViewSetPatch(generics.UpdateAPIView):
    serializer_class = QuotesSerializer
    queryset = Quotes.objects.all()
