from .data_fetcher import get_city_profile, get_all_cities, get_city_history  # 加一个 get_all_cities
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from .models import City, CityData
from .visualizer import calculate_score, make_radar, make_gauge, make_trend_chart
from .predictor import predict_city

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
    
    # 3. 生成图表
    radar_html = make_radar(data1, data2)
    gauge1 = make_gauge(city1, score1)
    gauge2 = make_gauge(city2, score2)

    # 4️⃣ 趋势图（新加）
    history1 = get_city_history(city1)
    if history1['status'] == 'success':
        trend_chart = make_trend_chart(city1, history1)
    else:
        trend_chart = '<p>暂无历史数据</p>'

    # 5️⃣ 预测（ML模块）
    prediction1 = predict_city(city1, 2027)
    
    
    # 4. 传给前端
    return render(request, "liveability/dashboard.html", {
        "city1": city1,
        "city2": city2,

        # 城市数据（用于显示详情）
        "data1": data1,
        "data2": data2,

        "score1": score1,
        "score2": score2,

        # 图表（注意变量名要与模板一致）
        "radar": radar_html,           # 模板中用 radar
        "gauge1": gauge1,              # 模板中用 gauge1
        "gauge2": gauge2,              # 模板中用 gauge2
        "trend_chart": trend_chart,     # 模板中用 trend_chart
        "prediction1": prediction1,     # 模板中用 prediction1
    })

def methodology(request):
    """方法论与数据来源说明页"""
    return render(request, "liveability/methodology.html")