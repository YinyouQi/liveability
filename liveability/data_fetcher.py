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
    包含静态指数 + 实时天气 + 实时空气质量
    """
    try:
        # 1. 从本地 CSV 读取静态数据（所有指数）
        static_data = _load_static_data(city_name_en)
        
        # 2. 从 API 获取实时数据（如果失败，返回占位数据）
        live_data = _fetch_live_data(city_name_en)
        
        return {
            'status': 'success',
            'city': city_name_en,
            'static_data': {
                'safety_index': static_data['safety_index'],
                'health_index': static_data['health_index'],
                'cost_of_living': static_data['cost_of_living'],
                'property_ratio': static_data['property_ratio'],
                'traffic_time': static_data['traffic_time'],
                'pollution_index': static_data['pollution_index'],
                'climate_index': static_data['climate_index']
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
                'cost_of_living': None,
                'property_ratio': None,
                'traffic_time': None,
                'pollution_index': None,
                'climate_index': None
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
    从 CSV 文件读取城市静态数据
    返回所有可用的 Numbeo 指数
    """
    import pandas as pd
    import os
    
    csv_path = os.path.join(os.path.dirname(__file__), 'data', 'numbeo_all_years.csv')
    
    try:
        df = pd.read_csv(csv_path)
        
        # 取每个城市最新年份的数据（2026年优先）
        df_latest = df.sort_values('Year', ascending=False).groupby('City').first().reset_index()
        
        # 查找匹配的城市（忽略大小写，支持部分匹配）
        city_lower = city_name_en.lower()
        
        # 方法1：精确匹配
        city_row = df_latest[df_latest['City'].str.lower() == city_lower]
        
        # 方法2：如果精确匹配找不到，尝试包含匹配
        if city_row.empty:
            city_row = df_latest[df_latest['City'].str.lower().str.contains(city_lower, na=False)]
        
        # 方法3：如果还找不到，尝试去掉括号内容后匹配
        if city_row.empty:
            df_latest['City_Simple'] = df_latest['City'].str.split(',').str[0].str.strip().str.lower()
            city_row = df_latest[df_latest['City_Simple'] == city_lower]
        
        if not city_row.empty:
            row = city_row.iloc[0]
            
            # 获取所有指数，转换为 float
            safety = row.get('Safety Index', 70.0)
            health = row.get('Health Care Index', 75.0)
            cost = row.get('Cost of Living Index', 70.0)
            property_ratio = row.get('Property Price to Income Ratio', 0)
            traffic = row.get('Traffic Commute Time Index', 0)
            pollution = row.get('Pollution Index', 0)
            climate = row.get('Climate Index', 0)
            
            # 类型转换
            if isinstance(safety, (np.integer, np.floating)):
                safety = float(safety)
            if isinstance(health, (np.integer, np.floating)):
                health = float(health)
            if isinstance(cost, (np.integer, np.floating)):
                cost = float(cost)
            if isinstance(property_ratio, (np.integer, np.floating)):
                property_ratio = float(property_ratio)
            if isinstance(traffic, (np.integer, np.floating)):
                traffic = float(traffic)
            if isinstance(pollution, (np.integer, np.floating)):
                pollution = float(pollution)
            if isinstance(climate, (np.integer, np.floating)):
                climate = float(climate)
            
            return {
                'safety_index': safety,
                'health_index': health,
                'cost_of_living': cost,
                'property_ratio': property_ratio,
                'traffic_time': traffic,
                'pollution_index': pollution,
                'climate_index': climate
            }
        else:
            print(f"警告: 未找到城市 '{city_name_en}'，返回默认值")
            return {
                'safety_index': 70.0,
                'health_index': 75.0,
                'cost_of_living': 70.0,
                'property_ratio': 0,
                'traffic_time': 0,
                'pollution_index': 0,
                'climate_index': 0
            }
            
    except Exception as e:
        print(f"读取CSV失败: {e}")
        return {
            'safety_index': 70.0,
            'health_index': 75.0,
            'cost_of_living': 70.0,
            'property_ratio': 0,
            'traffic_time': 0,
            'pollution_index': 0,
            'climate_index': 0
        }


def _fetch_live_data(city_name_en):
    """
    获取实时数据：天气 + AQI
    使用 OpenWeatherMap API + AQICN API
    """
    import requests
    
    # OpenWeatherMap API Key
    WEATHER_API_KEY = "9481998945f63ef76d37cbee612af58a"
    # AQICN API Token
    AQI_TOKEN = "670cca4f211cfd77bcdd0e1366c476f50d0cd591"
    
    # 初始化返回数据
    result = {
        'temp': 20,          # 默认温度
        'aqi': 50,           # 默认空气质量
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

        # 如果最终还是 None，强制兜底
        if result['aqi'] is None:
            result['aqi'] = 50
            
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
    返回简化的城市名（去掉国家后缀）
    """
    import pandas as pd
    import os
    
    csv_path = os.path.join(os.path.dirname(__file__), 'data', 'numbeo_all_years.csv')
    
    try:
        df = pd.read_csv(csv_path)
        # 取最新年份的唯一城市
        df_latest = df.sort_values('Year', ascending=False).groupby('City').first().reset_index()
        
        # 简化城市名（取逗号前的部分）
        cities = []
        for city in df_latest['City'].unique():
            simple_city = city.split(',')[0].strip()
            cities.append(simple_city)
        
        return sorted(set(cities))
        
    except Exception as e:
        print(f"读取城市列表失败: {e}")
        return []


def get_city_history(city_name_en):
    """
    获取城市历史数据（2023-2026），供成员C 做趋势图
    返回所有指数的时间序列
    """
    import pandas as pd
    import os
    
    csv_path = os.path.join(os.path.dirname(__file__), 'data', 'numbeo_all_years.csv')
    
    try:
        df = pd.read_csv(csv_path)
        
        # 查找匹配的城市
        city_lower = city_name_en.lower()
        
        # 方法1：精确匹配
        city_data = df[df['City'].str.lower() == city_lower]
        
        # 方法2：包含匹配
        if city_data.empty:
            city_data = df[df['City'].str.lower().str.contains(city_lower, na=False)]
        
        # 方法3：简化匹配
        if city_data.empty:
            df['City_Simple'] = df['City'].str.split(',').str[0].str.strip().str.lower()
            city_data = df[df['City_Simple'] == city_lower]
        
        if city_data.empty:
            return {'status': 'error', 'message': f'未找到城市 {city_name_en}'}
        
        # 按年份排序
        city_data = city_data.sort_values('Year')
        
        result = {
            'status': 'success',
            'city': city_name_en,
            'years_data': []
        }
        
        for _, row in city_data.iterrows():
            result['years_data'].append({
                'year': int(row['Year']),
                'safety_index': float(row.get('Safety Index', 0)),
                'health_index': float(row.get('Health Care Index', 0)),
                'cost_of_living': float(row.get('Cost of Living Index', 0)),
                'property_ratio': float(row.get('Property Price to Income Ratio', 0)),
                'traffic_time': float(row.get('Traffic Commute Time Index', 0)),
                'pollution_index': float(row.get('Pollution Index', 0)),
                'climate_index': float(row.get('Climate Index', 0))
            })
        
        return result
        
    except Exception as e:
        return {'status': 'error', 'message': str(e)}


def get_available_years():
    """
    返回数据中包含的所有年份
    """
    import pandas as pd
    import os
    
    csv_path = os.path.join(os.path.dirname(__file__), 'data', 'numbeo_all_years.csv')
    
    try:
        df = pd.read_csv(csv_path)
        years = sorted(df['Year'].unique().tolist())
        return years
    except Exception as e:
        print(f"读取年份失败: {e}")
        return []


if __name__ == "__main__":
    print("=" * 50)
    print("测试数据获取模块（Numbeo 2023-2026 多年度数据）")
    print("=" * 50)
    
    # 测试最新数据
    test_cities = ["London", "Shanghai", "New York"]
    
    for city in test_cities:
        print(f"\n--- 最新数据: {city} ---")
        result = get_city_profile(city)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    # 测试历史数据（趋势图）
    print("\n" + "=" * 50)
    print("测试历史数据（伦敦 2023-2026）")
    print("=" * 50)
    history = get_city_history("London")
    print(json.dumps(history, indent=2, ensure_ascii=False))
    
    # 显示可用年份和城市数量
    print("\n" + "=" * 50)
    print("可用年份:", get_available_years())
    print("城市数量:", len(get_all_cities()))

def get_city_prediction(city_name_en, predict_year=None):
    """
    获取城市预测数据（供前端使用）
    
    参数:
        city_name_en: 城市名
        predict_year: 预测年份（不传则默认最新年份+1）
    """
    try:
        from predictor import predict_city, get_available_predict_years
        
        # 如果没指定年份，自动用最新年份+1
        if predict_year is None:
            years_info = get_available_predict_years()
            predict_year = years_info['recommended_start']
        
        result = predict_city(city_name_en, predict_year)
        return result
        
    except ImportError:
        return {
            'status': 'error',
            'message': '预测模块未安装，请运行: pip install scikit-learn'
        }
    except Exception as e:
        return {
            'status': 'error',
            'message': str(e)
        }


def get_prediction_years():
    """
    获取可选择的预测年份列表（供前端下拉菜单）
    """
    try:
        from predictor import get_available_predict_years
        return get_available_predict_years()
    except ImportError:
        return {'years': [2027, 2028, 2029, 2030]}
