from .data_fetcher import get_city_profile, get_all_cities, get_city_history  # 加一个 get_all_cities
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.contrib import messages
from django.db.models import Q
from .models import City, CityData, FavoriteCity
from .visualizer import calculate_score, make_radar, make_gauge, make_trend_chart
from .predictor import predict_city

def city_search(request):
    """城市搜索页面"""
    query = request.GET.get('q', '').strip()
    search_results = []
    search_performed = False
    city_list = get_all_cities()  # 获取所有城市列表
    
    if query:
        search_performed = True
        # 获取所有城市列表
        all_cities = get_all_cities()
        
        # 模糊搜索匹配的城市
        search_results = [
            city for city in all_cities 
            if query.lower() in city.lower()
        ]
        
        # 限制结果数量，避免过多
        search_results = search_results[:20]
        
        # 为每个搜索结果获取简要数据
        cities_data = []
        for city in search_results:
            city_data = get_city_profile(city)
            if city_data['status'] == 'success':
                score = calculate_score(city_data)
                
                # 检查是否被当前用户收藏
                is_favorited = False
                if request.user.is_authenticated:
                    try:
                        city_obj = City.objects.get(name=city)
                        is_favorited = FavoriteCity.objects.filter(
                            user=request.user,
                            city=city_obj
                        ).exists()
                    except City.DoesNotExist:
                        pass
                
                cities_data.append({
                    'name': city,
                    'score': score,
                    'safety_index': city_data['static_data']['safety_index'],
                    'health_index': city_data['static_data']['health_index'],
                    'cost_of_living': city_data['static_data']['cost_of_living'],
                    'temperature': city_data['live_data']['temp'],
                    'aqi': city_data['live_data']['aqi'],
                    'weather_desc': city_data['live_data']['weather_desc'],
                    'is_favorited': is_favorited
                })
        
        # 按评分排序（高分在前）
        cities_data.sort(key=lambda x: x['score'], reverse=True)
        
        return render(request, 'liveability/city_search.html', {
            'query': query,
            'search_results': cities_data,
            'search_performed': search_performed,
            'result_count': len(cities_data),
            'city_list': city_list,  # 确保这一行有逗号
        })  # ← 这里确保括号正确闭合
    
    # 如果没有搜索词，显示空页面
    return render(request, 'liveability/city_search.html', {
        'query': query,
        'search_results': [],
        'search_performed': search_performed,
        'result_count': 0,
        'city_list': city_list,
    })


def city_detail(request, city_name):
    """城市详情页面"""
    # 获取城市数据
    city_data = get_city_profile(city_name)
    
    if city_data['status'] != 'success':
        # 如果获取失败，返回404或错误页面
        return render(request, 'liveability/city_not_found.html', {
            'city_name': city_name
        })
    
    # 计算评分
    score = calculate_score(city_data)
    
    # 获取历史数据用于趋势图
    history = get_city_history(city_name)
    trend_chart = None
    if history['status'] == 'success':
        trend_chart = make_trend_chart(city_name, history)
    
    # 获取预测数据
    prediction = predict_city(city_name, 2027)
    
    # 检查是否被收藏
    is_favorited = False
    if request.user.is_authenticated:
        try:
            city_obj, _ = City.objects.get_or_create(
                name=city_name,
                defaults={'country': 'Unknown', 'lat': 0.0, 'lon': 0.0}
            )
            is_favorited = FavoriteCity.objects.filter(
                user=request.user,
                city=city_obj
            ).exists()
        except:
            pass
    
    # 获取推荐对比城市（优先显示用户的收藏城市）
    similar_cities = []
    
    if request.user.is_authenticated:
        # 获取用户收藏的城市
        favorite_cities = FavoriteCity.objects.filter(
            user=request.user
        ).select_related('city').exclude(city__name=city_name)[:5]  # 排除当前城市，最多取5个
        
        similar_cities = [fav.city.name for fav in favorite_cities]
    
    # 如果用户没有收藏城市或收藏数量不足，用默认城市补充
    default_cities = ['London', 'New York', 'Shanghai', 'Sydney', 'Los Angeles']
    if len(similar_cities) < 5:
        # 添加默认城市，排除当前城市和已有的收藏城市
        for default_city in default_cities:
            if default_city != city_name and default_city not in similar_cities:
                similar_cities.append(default_city)
                if len(similar_cities) >= 5:
                    break
    
    return render(request, 'liveability/city_detail.html', {
        'city_name': city_name,
        'city_data': city_data,
        'score': score,
        'trend_chart': trend_chart,
        'prediction': prediction,
        'is_favorited': is_favorited,
        'similar_cities': similar_cities
    })

@login_required
def add_favorite(request, city_name):
    """添加城市到收藏"""
    try:
        # 获取或创建城市（确保城市在数据库中）
        city_obj, created = City.objects.get_or_create(
            name=city_name,
            defaults={
                'country': 'Unknown',  # 可以根据需要设置默认值
                'lat': 0.0,
                'lon': 0.0
            }
        )
        
        # 检查是否已经收藏
        favorite, created = FavoriteCity.objects.get_or_create(
            user=request.user,
            city=city_obj
        )
        
        if created:
            messages.success(request, f'成功收藏 {city_name}！')
        else:
            messages.info(request, f'{city_name} 已经在您的收藏列表中')
            
    except Exception as e:
        messages.error(request, f'收藏失败: {str(e)}')
    
    # 返回上一页
    return redirect(request.META.get('HTTP_REFERER', 'index'))


@login_required
def remove_favorite(request, city_name):
    """从收藏中移除城市"""
    try:
        # 获取城市对象
        city_obj = get_object_or_404(City, name=city_name)
        
        # 删除收藏记录
        FavoriteCity.objects.filter(
            user=request.user,
            city=city_obj
        ).delete()
        
        messages.success(request, f'已从收藏中移除 {city_name}')
        
    except Exception as e:
        messages.error(request, f'移除失败: {str(e)}')
    
    # 返回上一页
    return redirect(request.META.get('HTTP_REFERER', 'index'))


@login_required
def favorite_list(request):
    """显示用户的收藏列表"""
    favorites = FavoriteCity.objects.filter(user=request.user).order_by('-date_added')
    
    # 为每个收藏的城市获取数据
    favorite_cities_data = []
    for fav in favorites:
        city_data = get_city_profile(fav.city.name)
        if city_data['status'] == 'success':
            score = calculate_score(city_data)
            favorite_cities_data.append({
                'city': fav.city,
                'data': city_data,
                'score': score,
                'date_added': fav.date_added
            })
    
    return render(request, 'liveability/favorites.html', {
        'favorites': favorite_cities_data
    })



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
    # 确保城市在数据库中
    city_obj1, _ = City.objects.get_or_create(
        name=city1,
        defaults={'country': 'Unknown', 'lat': 0.0, 'lon': 0.0}
    )
    city_obj2, _ = City.objects.get_or_create(
        name=city2,
        defaults={'country': 'Unknown', 'lat': 0.0, 'lon': 0.0}
    )

    # 判断是否收藏
    is_favorited1 = False
    is_favorited2 = False

    if request.user.is_authenticated:
        is_favorited1 = FavoriteCity.objects.filter(
            user=request.user,
            city=city_obj1
        ).exists()
        is_favorited2 = FavoriteCity.objects.filter(
            user=request.user,
            city=city_obj2
        ).exists()
    
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

        "city_obj1": city_obj1,
        "city_obj2": city_obj2,
        "is_favorited1": is_favorited1,
        "is_favorited2": is_favorited2,
    })

def methodology(request):
    """方法论与数据来源说明页"""
    return render(request, "liveability/methodology.html")