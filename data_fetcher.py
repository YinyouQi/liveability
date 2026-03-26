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
    合并 train_us_new.csv 和 test_new.csv 两个数据集
    """
    import pandas as pd
    import os
    
    # 两个 CSV 文件路径
    csv_path1 = os.path.join(os.path.dirname(__file__), 'data', 'train_us_new.csv')
    csv_path2 = os.path.join(os.path.dirname(__file__), 'data', 'test_new.csv')
    
    try:
        # 读取两个 CSV 并合并
        df1 = pd.read_csv(csv_path1)
        df2 = pd.read_csv(csv_path2)
        df = pd.concat([df1, df2], ignore_index=True)
        
        # 按城市名分组，取最新数据（按 Year 和 Month 排序）
        # 先创建日期列用于排序
        month_to_num = {
            'January': 1, 'February': 2, 'March': 3, 'April': 4,
            'May': 5, 'June': 6, 'July': 7, 'August': 8,
            'September': 9, 'October': 10, 'November': 11, 'December': 12
        }
        df['Month_Num'] = df['Month'].map(month_to_num)
        df['Date'] = pd.to_datetime(df['Year'].astype(str) + '-' + df['Month_Num'].astype(str), format='%Y-%m')
        
        # 按城市分组，取最新的一条数据
        df_latest = df.sort_values('Date', ascending=False).groupby('City').first().reset_index()
        
        # 查找匹配的城市（忽略大小写）
        city_row = df_latest[df_latest['City'].str.lower() == city_name_en.lower()]
        
        if not city_row.empty:
            row = city_row.iloc[0]
            
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
                'safety_index': happiness * 10,
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
    使用 OpenWeatherMap API
    """
    # 你的 OpenWeatherMap API Key
    API_KEY = "9481998945f63ef76d37cbee612af58a"
    
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city_name_en}&appid={API_KEY}&units=metric"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            return {
                'temp': data['main']['temp'],
                'aqi': None,
                'weather_desc': data['weather'][0]['description']
            }
        else:
            print(f"天气 API 返回错误: {response.status_code}")
            return {
                'temp': None,
                'aqi': None,
                'weather_desc': 'Weather data unavailable'
            }
            
    except Exception as e:
        print(f"天气 API 调用失败: {e}")
        return {
            'temp': None,
            'aqi': None,
            'weather_desc': 'Weather API error'
        }

def get_all_cities():
    """
    返回所有城市列表，供前端下拉菜单使用
    """
    import pandas as pd
    import os
    
    csv_path1 = os.path.join(os.path.dirname(__file__), 'data', 'train_us_new.csv')
    csv_path2 = os.path.join(os.path.dirname(__file__), 'data', 'test_new.csv')
    
    try:
        df1 = pd.read_csv(csv_path1)
        df2 = pd.read_csv(csv_path2)
        df = pd.concat([df1, df2], ignore_index=True)
        
        # 获取所有唯一城市名，排序后返回
        cities = sorted(df['City'].unique().tolist())
        return cities
        
    except Exception as e:
        print(f"读取城市列表失败: {e}")
        return []

if __name__ == "__main__":
    print("=" * 50)
    print("测试数据获取模块")
    print("=" * 50)
    
    test_cities = ["London", "Shanghai", "New York"]
    
    for city in test_cities:
        print(f"\n--- 测试城市: {city} ---")
        result = get_city_profile(city)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        print()