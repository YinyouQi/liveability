from .data_fetcher import get_city_profile, get_all_cities  # 加一个 get_all_cities
from django.shortcuts import render
from django.http import JsonResponse
from django.http import HttpResponse
from .data_fetcher import get_city_profile   # data_feature.py
from .models import City, CityData
from .visualizer import calculate_score, make_radar, make_gauge

def fetch_city(request, city_name):
    data = get_city_profile(city_name)

    if data['status'] != 'success':
        return JsonResponse(data)
    
    city_obj, _ = City.objects.get_or_create(name=city_name)

    CityData.objects.update_or_create(
        city=city_obj,
        defaults={
            "temp": data['live_data']['temp'],
            "aqi": data['live_data']['aqi'],
            "weather_desc": data['live_data']['weather_desc'],
            "safety_index": data['static_data']['safety_index'],
            "health_index": data['static_data']['health_index'],
            "cost_of_living": data['static_data']['cost_of_living'],
        }
    )

    return JsonResponse(data)

def index(request):
    """主页"""
    # 调用 A 的函数拿到城市列表 (如 ['London', 'Tokyo', ...])
    cities = get_all_cities() 
    # 传给 index.html
    return render(request, 'liveability/index.html', {'city_list': cities})

def city_dashboard(request, city1, city2):
    """城市对比页面"""
    # 1. 获取数据
    data1 = get_city_profile(city1)
    data2 = get_city_profile(city2)
    
    # 2. 计算评分
    score1 = calculate_score(data1)
    score2 = calculate_score(data2)
    
    # 临时方案：用简单分数代替
    # score1 = 75  # 临时占位
    # score2 = 80  # 临时占位
    
    # 3. 生成图表
    radar_html = make_radar(data1, data2)
    gauge1 = make_gauge(city1, score1)
    gauge2 = make_gauge(city2, score2)
    
    # 临时方案：用空字符串
    # radar_html = ""
    # gauge1 = ""
    # gauge2 = ""
    
    # 4. 传给前端
    return render(request, "liveability/dashboard.html", {
        "city1": city1,
        "city2": city2,
        "data1": data1,
        "data2": data2,
        "score1": score1,
        "score2": score2,
        "radar": radar_html,
        "gauge1": gauge1,
        "gauge2": gauge2,
    })