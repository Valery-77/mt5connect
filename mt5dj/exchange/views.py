from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from .models import Exchange


def index(request):
    if request.method == 'GET':
        try:
            exchange = get_object_or_404(Exchange, id=5)
            if not exchange.isApiKeyActive:
                commentary = 'Ключ APi истек'
                exchange.commentary = commentary
                exchange.save(update_fields=["commentary"])
                return HttpResponse(commentary)
            elif not exchange.connectExchange:
                commentary = 'Нет связи с биржей'
                exchange.commentary = commentary
                exchange.save(update_fields=["commentary"])
                return HttpResponse(commentary)
            elif not exchange.connectExchange and not exchange.isApiKeyActive:
                commentary = 'Нет связи с биржей и ключ APi истек'
                exchange.commentary = commentary
                exchange.save(update_fields=["commentary"])
                return HttpResponse(commentary)
            else:
                commentary = 'на редкость все хорошо'
                exchange.commentary = commentary
                exchange.save(update_fields=["commentary"])
                return HttpResponse(commentary)
        except Exception as e:
            return HttpResponse(e)
