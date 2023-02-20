from django.contrib import admin
from .models import StockParameters, StockTicker

# Register your models here.
admin.site.register(StockParameters)
admin.site.register(StockTicker)
