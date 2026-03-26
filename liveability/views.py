from django.shortcuts import render
from django.http import JsonResponse
from django.http import HttpResponse
from .data_fetcher import get_city_profile   # data_feature.py


def fetch_city(request, city_name):
    data = get_city_profile(city_name)
    return JsonResponse(data)

def home(request):
    return HttpResponse("Liveability Home Page")