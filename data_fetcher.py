"""
数据获取模块 - 负责所有底层数据获取与清洗
参考书单：第16章（CSV）、第17章（API）
"""

import csv
import requests
import json
from datetime import datetime


def get_city_data(city_name):
    """
    获取城市综合数据（静态CSV + 实时API）
    返回统一格式的数据字典
    """
    # TODO: 后续替换为真实CSV数据
    # 当前为 Mock 数据，供队友联调
    data = {
        "city": city_name,
        "healthcare_score": 85,
        "safety_score": 78,
        "cost_of_living": 65,
        "weather": {
            "temp": 22,
            "condition": "Sunny",
            "humidity": 60
        },
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    return data


def get_weather_data(city_name):
    """
    获取实时天气数据
    TODO: 接入 OpenWeatherMap API
    """
    # Mock 天气数据
    weather_data = {
        "city": city_name,
        "temp": 22,
        "feels_like": 21,
        "humidity": 60,
        "pressure": 1013,
        "condition": "Sunny"
    }
    return weather_data


def load_csv_data(file_path):
    """
    从CSV文件加载城市数据
    TODO: 从 Kaggle 下载城市指数数据集
    """
    # Mock CSV 数据
    return {
        "healthcare_index": 85.2,
        "safety_index": 78.5,
        "cost_of_living_index": 65.3,
        "pollution_index": 42.1
    }


if __name__ == "__main__":
    # 测试代码
    print("测试数据获取模块...")
    test_data = get_city_data("Shanghai")
    print(json.dumps(test_data, indent=2, ensure_ascii=False))