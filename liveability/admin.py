from django.contrib import admin

# Register your models here.
from .models import City, CityData, Preference, FavoriteCity

admin.site.register(City)
admin.site.register(CityData)
admin.site.register(Preference)
admin.site.register(FavoriteCity)