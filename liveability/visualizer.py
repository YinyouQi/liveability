from .data_fetcher import get_city_profile
import plotly.graph_objects as go
import plotly.express as px


# ===== 1. 宜居度评分 =====
def calculate_score(city_profile):
    static = city_profile['static_data']
    live = city_profile['live_data']
    
    # 静态数据（9个指标）
    safety = static.get('safety_index', 50)
    health = static.get('health_index', 50)
    cost = static.get('cost_of_living', 50)
    property_ratio = static.get('property_ratio', 50)
    traffic_time = static.get('traffic_time', 50)
    pollution = static.get('pollution_index', 50)
    climate = static.get('climate_index', 50)
    
    # 实时数据
    temp = live['temp']
    aqi = live['aqi']
    
    # 温度评分（20-25°C 最佳）
    if temp is None:
        temp = 20
    if 20 <= temp <= 25:
        temp_score = 100
    else:
        temp_score = 100 - min(abs(temp - 22.5) * 5, 100)
    
    # AQI 评分
    if aqi is None:
        aqi = 50
    if aqi <= 50:
        aqi_score = 100
    elif aqi <= 100:
        aqi_score = 80
    elif aqi <= 150:
        aqi_score = 60
    else:
        aqi_score = 40
    
    # 其他指标转成 0-100 分（值越低越好）
    cost_score = max(0, 100 - cost)
    property_score = max(0, 100 - property_ratio)
    traffic_score = max(0, 100 - traffic_time)
    pollution_score = max(0, 100 - pollution)
    climate_score = climate  # 气候指数已经是 0-100
    
    # 加权总分（9个维度，根据重要性调整权重）
    total = (temp_score * 0.12 +
             aqi_score * 0.12 +
             safety * 0.12 +
             health * 0.12 +
             cost_score * 0.12 +
             property_score * 0.08 +
             traffic_score * 0.08 +
             pollution_score * 0.12 +
             climate_score * 0.12)
    
    return round(total, 1)

# ===== 2. 雷达图 =====
def make_radar(city1_profile, city2_profile):
    """
    生成 9 维雷达图对比两个城市
    """
    categories = ['温度', '空气质量', '安全指数', '医疗指数', '生活成本', 
                  '房价收入比', '通勤时间', '污染指数', '气候指数']
    
    static1 = city1_profile['static_data']
    live1 = city1_profile['live_data']
    
    # 第一个城市的 9 个维度值
    city1_values = [
        live1.get('temp') or 20,                                    # 温度
        100 - (live1.get('aqi') or 50),                               # 空气质量（转成越高越好）
        static1.get('safety_index', 50),                  # 安全指数
        static1.get('health_index', 50),                  # 医疗指数
        100 - static1.get('cost_of_living', 50),          # 生活成本（越低越好）
        100 - static1.get('property_ratio', 50),          # 房价收入比（越低越好）
        100 - static1.get('traffic_time', 50),            # 通勤时间（越低越好）
        100 - static1.get('pollution_index', 50),         # 污染指数（越低越好）
        static1.get('climate_index', 50)                  # 气候指数
    ]
    
    static2 = city2_profile['static_data']
    live2 = city2_profile['live_data']
    
    # 第二个城市的 9 个维度值
    city2_values = [
        live2['temp'],
        100 - live2['aqi'],
        static2.get('safety_index', 50),
        static2.get('health_index', 50),
        100 - static2.get('cost_of_living', 50),
        100 - static2.get('property_ratio', 50),
        100 - static2.get('traffic_time', 50),
        100 - static2.get('pollution_index', 50),
        static2.get('climate_index', 50)
    ]
    
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=city1_values, 
        theta=categories, 
        fill='toself', 
        name=city1_profile['city'],
        line=dict(color='#3498db', width=2),
        fillcolor='rgba(52, 152, 219, 0.3)'
    ))
    fig.add_trace(go.Scatterpolar(
        r=city2_values, 
        theta=categories, 
        fill='toself', 
        name=city2_profile['city'],
        line=dict(color='#e74c3c', width=2),
        fillcolor='rgba(231, 76, 60, 0.3)'
    ))
    
    fig.update_layout(
        title=f"{city1_profile['city']} vs {city2_profile['city']} 宜居度对比",
        title_font_size=20,
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100], gridcolor='#e9ecef'),
            angularaxis=dict(tickfont=dict(size=10)),
            bgcolor='#f8f9fa'
        ),
        paper_bgcolor='#f8f9fa',
        height=600,
        width=800,
        showlegend=True,
        legend=dict(x=0.9, y=1.1)
    )
    return fig.to_html()

#3.仪表盘图
def make_gauge(city_name, score):
    """
    Generate a gauge chart for a city's livability score
    """
    import plotly.graph_objects as go
    
    # 根据分数设置颜色
    if score >= 80:
        bar_color = "#2ecc71"
        title_color = "#27ae60"
        steps = [
            {'range': [0, 50], 'color': "#e74c3c"},
            {'range': [50, 70], 'color': "#f1c40f"},
            {'range': [70, 80], 'color': "#2ecc71"},
            {'range': [80, 100], 'color': "#27ae60"}
        ]
    elif score >= 70:
        bar_color = "#2ecc71"
        title_color = "#f39c12"
        steps = [
            {'range': [0, 50], 'color': "#e74c3c"},
            {'range': [50, 70], 'color': "#f1c40f"},
            {'range': [70, 100], 'color': "#2ecc71"}
        ]
    elif score >= 50:
        bar_color = "#f1c40f"
        title_color = "#e67e22"
        steps = [
            {'range': [0, 50], 'color': "#e74c3c"},
            {'range': [50, 70], 'color': "#f1c40f"},
            {'range': [70, 100], 'color': "#95a5a6"}
        ]
    else:
        bar_color = "#e74c3c"
        title_color = "#c0392b"
        steps = [
            {'range': [0, 50], 'color': "#e74c3c"},
            {'range': [50, 70], 'color': "#f1c40f"},
            {'range': [70, 100], 'color': "#95a5a6"}
        ]
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        title={
            'text': f"{city_name}<br>Livability Score",
            'font': {'size': 24, 'color': title_color}
        },
        number={
            'font': {'size': 48, 'color': bar_color},
            'suffix': " pts"
        },
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 2, 'tickcolor': "#34495e"},
            'bar': {'color': bar_color, 'thickness': 0.3},
            'bgcolor': "#f8f9fa",
            'borderwidth': 2,
            'bordercolor': "#bdc3c7",
            'steps': steps,
            'threshold': {
                'line': {'color': "#2c3e50", 'width': 4},
                'thickness': 0.75,
                'value': score
            }
        }
    ))
    
    fig.update_layout(height=400, width=500, paper_bgcolor="#f8f9fa")
    return fig.to_html()


if __name__ == '__main__':
    from data_fetcher import get_city_profile
    
    # 测试东京
    tokyo = get_city_profile('Tokyo')
    score = calculate_score(tokyo)
    print(f"东京评分: {score}")
    
    # 生成仪表盘图
    gauge_html = make_gauge('Tokyo', score)
    with open('gauge_tokyo.html', 'w', encoding='utf-8') as f:
        f.write(gauge_html)
    print("仪表盘图已生成: gauge_tokyo.html")
    
    # 生成雷达图
    london = get_city_profile('London')
    radar_html = make_radar(tokyo, london)
    with open('radar_tokyo_london.html', 'w', encoding='utf-8') as f:
        f.write(radar_html)
    print("雷达图已生成: radar_tokyo_london.html")