"""
数据获取模块 - 负责所有底层数据获取与清洗
对接接口：get_city_profile(city_name_en)
"""

import csv
import requests
import json
from datetime import datetime


def get_city_profile(city_name_en):
    """
    接收英文城市名，返回合并后的数据字典。
    如果 API 失败，要有容错机制。
    """
    try:
        # 1. 从本地 CSV 读取静态数据
        static_data = _load_static_data(city_name_en)
        
        # 2. 从 API 获取实时数据（如果失败，返回占位数据）
        live_data = _fetch_live_data(city_name_en)
        
        return {
            'status': 'success',
            'city': city_name_en,
            'static_data': static_data,
            'live_data': live_data
        }
        
    except Exception as e:
        # 容错：返回错误状态，但尽量提供占位数据
        return {
            'status': 'error',
            'city': city_name_en,
            'static_data': {
                'safety_index': None,
                'health_index': None,
                'cost_of_living': None
            },
            'live_data': {
                'temp': None,
                'aqi': None,
                'weather_desc': 'Data unavailable'
            },
            'error_message': str(e)
        }


def _load_static_data(city_name_en):
    """
    从 CSV 文件读取城市静态数据（安全指数、健康指数、生活成本）
    TODO: 从 Kaggle 下载 Numbeo Quality of Life 数据集
    目前返回 Mock 数据
    """
    # TODO: 替换为真实 CSV 读取逻辑
    # with open('data/cities.csv', 'r', encoding='utf-8') as f:
    #     reader = csv.DictReader(f)
    #     for row in reader:
    #         if row['city'] == city_name_en:
    #             return {
    #                 'safety_index': float(row['safety_index']),
    #                 'health_index': float(row['health_index']),
    #                 'cost_of_living': float(row['cost_of_living'])
    #             }
    
    # Mock 数据（供队友联调）
    mock_data = {
        'London': {'safety_index': 75.5, 'health_index': 82.1, 'cost_of_living': 88.0},
        'Shanghai': {'safety_index': 78.5, 'health_index': 85.2, 'cost_of_living': 65.3},
        'New York': {'safety_index': 68.2, 'health_index': 79.5, 'cost_of_living': 95.0}
    }
    
    return mock_data.get(city_name_en, {
        'safety_index': 70.0,
        'health_index': 75.0,
        'cost_of_living': 70.0
    })


def _fetch_live_data(city_name_en):
    """
    获取实时数据：天气 + AQI
    TODO: 
        1. 注册 OpenWeatherMap API: https://openweathermap.org/api
        2. 注册 AQICN API: https://aqicn.org/api/
    目前返回 Mock 数据
    """
    # TODO: 替换为真实 API 调用
    # try:
    #     weather_url = f"https://api.openweathermap.org/data/2.5/weather?q={city_name_en}&appid=YOUR_API_KEY&units=metric"
    #     weather_response = requests.get(weather_url, timeout=5)
    #     weather_data = weather_response.json()
    #     
    #     aqi_url = f"https://api.waqi.info/feed/{city_name_en}/?token=YOUR_API_KEY"
    #     aqi_response = requests.get(aqi_url, timeout=5)
    #     aqi_data = aqi_response.json()
    #     
    #     return {
    #         'temp': weather_data['main']['temp'],
    #         'aqi': aqi_data['data']['aqi'],
    #         'weather_desc': weather_data['weather'][0]['description']
    #     }
    # except Exception as e:
    #     # API 失败时返回占位数据
    #     return {
    #         'temp': None,
    #         'aqi': None,
    #         'weather_desc': 'API error'
    #     }
    
    # Mock 数据（供队友联调）
    mock_live_data = {
        'London': {'temp': 15.2, 'aqi': 45, 'weather_desc': 'Clouds'},
        'Shanghai': {'temp': 22.0, 'aqi': 65, 'weather_desc': 'Sunny'},
        'New York': {'temp': 18.5, 'aqi': 38, 'weather_desc': 'Clear'}
    }
    
    return mock_live_data.get(city_name_en, {
        'temp': 20.0,
        'aqi': 50,
        'weather_desc': 'Unknown'
    })


if __name__ == "__main__":
    # 测试代码
    print("测试数据获取模块...")
    test_city = "London"
    result = get_city_profile(test_city)
    print(json.dumps(result, indent=2, ensure_ascii=False))