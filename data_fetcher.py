"""
数据获取模块 - 负责所有底层数据获取与清洗
对接接口：get_city_profile(city_name_en)
"""

import json
import os
import pandas as pd
import numpy as np
import requests
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
            'static_data': {
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
    使用新数据集：livable_cities.csv
    """
    import pandas as pd
    import os
    
    # CSV 文件路径
    csv_path = os.path.join(os.path.dirname(__file__), 'data', 'livable_cities.csv')
    
    try:
        # 读取 CSV
        df = pd.read_csv(csv_path)
        
        # 查找匹配的城市（忽略大小写）
        city_row = df[df['City'].str.lower() == city_name_en.lower()]
        
        if not city_row.empty:
            row = city_row.iloc[0]
            
            # 获取各项指标，转换为 float
            safety = row.get('Safety Index', 70.0)
            if isinstance(safety, (np.integer, np.floating)):
                safety = float(safety)
            
            health = row.get('Health Care Index', 75.0)
            if isinstance(health, (np.integer, np.floating)):
                health = float(health)
            
            cost = row.get('Cost of Living Index', 70.0)
            if isinstance(cost, (np.integer, np.floating)):
                cost = float(cost)
            
            return {
                'safety_index': safety,
                'health_index': health,
                'cost_of_living': cost
            }
        else:
            print(f"警告: 未找到城市 '{city_name_en}'，返回默认值")
            return {
                'safety_index': 70.0,
                'health_index': 75.0,
                'cost_of_living': 70.0
            }
            
    except Exception as e:
        print(f"读取CSV失败: {e}")
        return {
            'safety_index': 70.0,
            'health_index': 75.0,
            'cost_of_living': 70.0
        }


def _fetch_live_data(city_name_en):
    """
    获取实时数据：天气 + AQI
    使用 OpenWeatherMap API + AQICN API
    """
    import requests
    
    # OpenWeatherMap API Key
    WEATHER_API_KEY = "9481998945f63ef76d37cbee612af58a"  # 正确的 Key
    # AQICN API Token
    AQI_TOKEN = "670cca4f211cfd77bcdd0e1366c476f50d0cd591"
    
    # 初始化返回数据
    result = {
        'temp': None,
        'aqi': None,
        'weather_desc': 'Weather data unavailable'
    }
    
    # 1. 获取天气数据
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city_name_en}&appid={WEATHER_API_KEY}&units=metric"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            result['temp'] = data['main']['temp']
            result['weather_desc'] = data['weather'][0]['description']
        else:
            print(f"天气 API 返回错误: {response.status_code}")
    except Exception as e:
        print(f"天气 API 调用失败: {e}")
    
    # 2. 获取空气质量数据
    if AQI_TOKEN and AQI_TOKEN != "YOUR_AQI_TOKEN_HERE":
        try:
            aqi_url = f"https://api.waqi.info/feed/{city_name_en}/?token={AQI_TOKEN}"
            response = requests.get(aqi_url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'ok':
                    result['aqi'] = data['data']['aqi']
                else:
                    print(f"AQI API 返回错误: {data.get('data')}")
            else:
                print(f"AQI API 返回状态码: {response.status_code}")
        except Exception as e:
            print(f"AQI API 调用失败: {e}")
    else:
        # 使用占位数据
        mock_aqi = {
            'london': 45, 'shanghai': 65, 'new york': 38,
            'beijing': 120, 'tokyo': 55, 'paris': 42
        }
        city_key = city_name_en.lower()
        result['aqi'] = mock_aqi.get(city_key, 50)
    
    return result


def get_all_cities():
    """
    返回所有城市列表，供前端下拉菜单使用
    """
    import pandas as pd
    import os
    
    csv_path = os.path.join(os.path.dirname(__file__), 'data', 'livable_cities.csv')
    
    try:
        df = pd.read_csv(csv_path)
        # 获取所有唯一城市名，排序后返回
        cities = sorted(df['City'].unique().tolist())
        return cities
        
    except Exception as e:
        print(f"读取城市列表失败: {e}")
        return []


if __name__ == "__main__":
    print("=" * 50)
    print("测试数据获取模块（新数据集：150个全球城市）")
    print("=" * 50)
    
    test_cities = ["London", "Shanghai", "New York", "Tokyo", "Paris", "Beijing"]
    
    for city in test_cities:
        print(f"\n--- 测试城市: {city} ---")
        result = get_city_profile(city)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        print()