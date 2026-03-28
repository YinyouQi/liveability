"""
机器学习预测模块
基于历史数据预测未来城市宜居指数
支持用户自定义预测年份
"""

import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
import os
import json


def load_city_history(city_name_en):
    """
    从 CSV 加载指定城市的历史数据
    """
    csv_path = os.path.join(os.path.dirname(__file__), 'data', 'numbeo_all_years.csv')
    
    try:
        df = pd.read_csv(csv_path)
        
        # 匹配城市
        city_lower = city_name_en.lower()
        city_data = df[df['City'].str.lower().str.contains(city_lower, na=False)]
        
        if city_data.empty:
            df['City_Simple'] = df['City'].str.split(',').str[0].str.strip().str.lower()
            city_data = df[df['City_Simple'] == city_lower]
        
        if city_data.empty:
            return None
        
        # 按年份排序
        city_data = city_data.sort_values('Year')
        
        # 提取历史数据
        history = {
            'years': city_data['Year'].tolist(),
            'safety': city_data['Safety Index'].tolist(),
            'health': city_data['Health Care Index'].tolist(),
            'cost': city_data['Cost of Living Index'].tolist(),
            'pollution': city_data['Pollution Index'].tolist(),
            'climate': city_data['Climate Index'].tolist()
        }
        
        return history
        
    except Exception as e:
        print(f"加载数据失败: {e}")
        return None


def predict_linear(years, values, predict_year):
    """
    使用线性回归预测
    """
    if len(years) < 2:
        return values[-1] if values else 0
    
    # 准备数据
    X = np.array(years).reshape(-1, 1)
    y = np.array(values)
    
    # 训练模型
    model = LinearRegression()
    model.fit(X, y)
    
    # 预测
    prediction = model.predict([[predict_year]])[0]
    
    return round(prediction, 1)


def predict_polynomial(years, values, predict_year, degree=2):
    """
    使用多项式回归预测（更准确）
    """
    if len(years) < 3:
        return predict_linear(years, values, predict_year)
    
    # 准备数据
    X = np.array(years).reshape(-1, 1)
    y = np.array(values)
    
    # 创建多项式特征
    poly = PolynomialFeatures(degree=degree)
    X_poly = poly.fit_transform(X)
    
    # 训练模型
    model = LinearRegression()
    model.fit(X_poly, y)
    
    # 预测
    X_pred = np.array([[predict_year]])
    X_pred_poly = poly.transform(X_pred)
    prediction = model.predict(X_pred_poly)[0]
    
    return round(prediction, 1)


def predict_city(city_name_en, predict_year, method='polynomial'):
    """
    预测城市未来指数
    
    参数:
        city_name_en: 城市名
        predict_year: 预测年份（用户自定义）
        method: 预测方法 'linear' 或 'polynomial'
    
    返回:
        dict: 预测结果
    """
    # 加载历史数据
    history = load_city_history(city_name_en)
    
    if history is None:
        return {
            'status': 'error',
            'message': f'未找到城市 {city_name_en}',
            'city': city_name_en
        }
    
    years = history['years']
    last_year = years[-1]
    
    # 检查预测年份是否合理
    if predict_year <= last_year:
        return {
            'status': 'warning',
            'message': f'预测年份 {predict_year} 不晚于最新数据年份 {last_year}，返回最新实际值',
            'city': city_name_en,
            'predict_year': predict_year,
            'latest_year': last_year,
            'latest_data': {
                'safety_index': history['safety'][-1],
                'health_index': history['health'][-1],
                'cost_of_living': history['cost'][-1],
                'pollution_index': history['pollution'][-1],
                'climate_index': history['climate'][-1]
            }
        }
    
    # 选择预测方法
    if method == 'linear':
        predict_func = predict_linear
    else:
        predict_func = predict_polynomial
    
    # 预测各项指数
    predictions = {
        'safety_index': predict_func(years, history['safety'], predict_year),
        'health_index': predict_func(years, history['health'], predict_year),
        'cost_of_living': predict_func(years, history['cost'], predict_year),
        'pollution_index': predict_func(years, history['pollution'], predict_year),
        'climate_index': predict_func(years, history['climate'], predict_year)
    }
    
    # 获取最新实际值
    latest = {
        'safety_index': history['safety'][-1],
        'health_index': history['health'][-1],
        'cost_of_living': history['cost'][-1],
        'pollution_index': history['pollution'][-1],
        'climate_index': history['climate'][-1],
        'year': last_year
    }
    
    # 计算变化趋势
    trends = {}
    for key in predictions:
        diff = predictions[key] - latest[key]
        trends[key] = {
            'change': round(diff, 1),
            'direction': 'up' if diff > 0 else 'down' if diff < 0 else 'stable'
        }
    
    return {
        'status': 'success',
        'city': city_name_en,
        'predict_year': predict_year,
        'latest_year': last_year,
        'latest_data': latest,
        'predictions': predictions,
        'trends': trends,
        'method': method
    }


def get_available_predict_years():
    """
    获取可预测的年份范围（基于最新数据年份 + 1 到 +10）
    """
    import pandas as pd
    import os
    
    csv_path = os.path.join(os.path.dirname(__file__), 'data', 'numbeo_all_years.csv')
    
    try:
        df = pd.read_csv(csv_path)
        latest_year = df['Year'].max()
        
        # 建议预测未来 1-10 年
        start_year = latest_year + 1
        end_year = latest_year + 10
        
        return {
            'latest_year': latest_year,
            'recommended_start': start_year,
            'recommended_end': end_year,
            'years': list(range(start_year, end_year + 1))
        }
    except Exception as e:
        print(f"读取年份失败: {e}")
        return {'years': [2027, 2028, 2029, 2030]}


def predict_city_trend(city_name_en, start_year, end_year):
    """
    预测城市未来多年的趋势
    
    参数:
        city_name_en: 城市名
        start_year: 开始年份
        end_year: 结束年份
    
    返回:
        list: 每年预测数据
    """
    results = []
    for year in range(start_year, end_year + 1):
        pred = predict_city(city_name_en, year, method='polynomial')
        if pred['status'] == 'success':
            results.append({
                'year': year,
                'safety_index': pred['predictions']['safety_index'],
                'health_index': pred['predictions']['health_index'],
                'cost_of_living': pred['predictions']['cost_of_living'],
                'pollution_index': pred['predictions']['pollution_index'],
                'climate_index': pred['predictions']['climate_index']
            })
    
    return results


if __name__ == "__main__":
    print("=" * 50)
    print("机器学习预测模块测试")
    print("=" * 50)
    
    # 获取可预测年份范围
    years_info = get_available_predict_years()
    print(f"\n最新数据年份: {years_info['latest_year']}")
    print(f"推荐预测范围: {years_info['recommended_start']} - {years_info['recommended_end']}")
    
    # 测试多个年份
    print("\n--- 预测 London 未来多年 ---")
    city = "London"
    
    for year in [2027, 2028, 2029, 2030]:
        result = predict_city(city, year)
        if result['status'] == 'success':
            print(f"\n{year}年预测:")
            print(f"  安全指数: {result['predictions']['safety_index']}")
            print(f"  医疗指数: {result['predictions']['health_index']}")
            print(f"  趋势: 安全指数 {result['trends']['safety_index']['direction']} {abs(result['trends']['safety_index']['change'])}点")
    
    # 测试趋势预测
    print("\n" + "=" * 50)
    print("London 2027-2030 趋势")
    print("=" * 50)
    trend = predict_city_trend("London", 2027, 2030)
    if trend:
        for year_data in trend:
            print(f"{year_data['year']}: 安全指数 {year_data['safety_index']}, 医疗指数 {year_data['health_index']}")