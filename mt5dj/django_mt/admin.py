from django.contrib import admin
from .models import InvestorModel, LiederModel
# Register your models here.
admin.site.register(LiederModel)
admin.site.register(InvestorModel)