"""
数据获取模块 - 负责所有底层数据获取与清洗
对接接口：get_city_profile(city_name_en)
"""

import json
import os
import pandas as pd
import numpy as np
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
            'status': 'success',  # 成功状态
            'city': city_name_en,
            'static_data': {       # 注意：是 static_data
                'safety_index': static_data['safety_index'],
                'health_index': static_data['health_index'],
                'cost_of_living': static_data['cost_of_living']
            },
            'live_data': {
                'temp': live_data['temp'],
                'aqi': live_data['aqi'],
                'weather_desc': live_data['weather_desc']
            }
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
    """
    # CSV 文件路径
    csv_path = os.path.join(os.path.dirname(__file__), 'data', 'train_us_new.csv')
    
    try:
        # 读取 CSV
        df = pd.read_csv(csv_path)
        
        # 查找匹配的城市（忽略大小写）
        city_row = df[df['City'].str.lower() == city_name_en.lower()]
        
        if not city_row.empty:
            row = city_row.iloc[0]
            
            # 获取数值并转换为 Python 原生类型（解决 JSON 序列化问题）
            happiness = row.get('Happiness_Score', 70.0)
            if isinstance(happiness, (np.integer, np.floating)):
                happiness = float(happiness)
            
            health = row.get('Health_Index', 75.0)
            if isinstance(health, (np.integer, np.floating)):
                health = float(health)
            
            cost = row.get('Cost_of_Living_Index', 70.0)
            if isinstance(cost, (np.integer, np.floating)):
                cost = float(cost)
            
            return {
               'safety_index': happiness * 10,  # 用幸福指数替代，缩放到0-100
                'health_index': health,
                'cost_of_living': cost
            }
        else:
            # 城市不存在，返回默认值
            print(f"警告: 未找到城市 '{city_name_en}'，返回默认值")
            return {
                'safety_index': 70.0,
                'health_index': 75.0,
                'cost_of_living': 70.0
            }
            
    except Exception as e:
        print(f"读取CSV失败: {e}")
        # 返回 Mock 数据
        return {
            'safety_index': 70.0,
            'health_index': 75.0,
            'cost_of_living': 70.0
        }


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
    #     import requests
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
        'london': {'temp': 15.2, 'aqi': 45, 'weather_desc': 'Clouds'},
        'shanghai': {'temp': 22.0, 'aqi': 65, 'weather_desc': 'Sunny'},
        'new york': {'temp': 18.5, 'aqi': 38, 'weather_desc': 'Clear'},
        'beijing': {'temp': 18.0, 'aqi': 120, 'weather_desc': 'Haze'},
        'tokyo': {'temp': 20.0, 'aqi': 55, 'weather_desc': 'Clear'},
        'paris': {'temp': 16.0, 'aqi': 42, 'weather_desc': 'Clouds'}
    }
    
    city_key = city_name_en.lower()
    if city_key in mock_live_data:
        return mock_live_data[city_key]
    else:
        return {
            'temp': 20.0,
            'aqi': 50,
            'weather_desc': 'Unknown'
        }


if __name__ == "__main__":
    # 测试代码
    print("=" * 50)
    print("测试数据获取模块")
    print("=" * 50)
    
    # 测试几个城市
    test_cities = ["London", "Shanghai", "New York", "Beijing"]
    
    for city in test_cities:
        print(f"\n--- 测试城市: {city} ---")
        result = get_city_profile(city)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        print()