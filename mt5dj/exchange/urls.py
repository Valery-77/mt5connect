from django.urls import path

from .views import QuotesViewSetPatch, index

urlpatterns = [
    path('', index, name='name'),
    path('update/<int:pk>/', QuotesViewSetPatch.as_view()),
]