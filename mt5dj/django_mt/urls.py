from django.urls import path
from .views import InvestorView

urlpatterns = [
    path('investors/', InvestorView.as_view(), name='investors'),
]
