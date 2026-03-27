from data_fetcher import get_city_profile
import plotly.graph_objects as go
import plotly.express as px


# ===== 1. 宜居度评分 =====
def calculate_score(city_profile):
    static = city_profile['static_data']
    live = city_profile['live_data']
    
    safety = static['safety_index']
    health = static['health_index']
    cost = static['cost_of_living']
    temp = live['temp']
    aqi = live['aqi']

    if 20 <= temp <= 25:
        temp_score = 100
    else:
        temp_score = 100 - min(abs(temp - 22.5) * 5, 100)
    
    if aqi <= 50:
        aqi_score = 100
    elif aqi <= 100:
        aqi_score = 80
    elif aqi <= 150:
        aqi_score = 60
    else:
        aqi_score = 40
    
    cost_score = max(0, 100 - cost)
    
    total = (temp_score * 0.2 + aqi_score * 0.2 + safety * 0.2 + health * 0.2 + cost_score * 0.2)
    return round(total, 1)

# ===== 2. 雷达图 =====
def make_radar(city1_profile, city2_profile):
    categories = ['温度', '空气质量', '安全指数', '健康指数', '生活成本']
    
    static1 = city1_profile['static_data']
    live1 = city1_profile['live_data']
    city1_values = [
        live1['temp'],
        100 - live1['aqi'],
        static1['safety_index'],
        static1['health_index'],
        100 - static1['cost_of_living']
    ]
    
    static2 = city2_profile['static_data']
    live2 = city2_profile['live_data']
    city2_values = [
        live2['temp'],
        100 - live2['aqi'],
        static2['safety_index'],
        static2['health_index'],
        100 - static2['cost_of_living']
    ]
    
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=city1_values, theta=categories, fill='toself', name=city1_profile['city']))
    fig.add_trace(go.Scatterpolar(r=city2_values, theta=categories, fill='toself', name=city2_profile['city']))
    
    fig.update_layout(
        title=f"{city1_profile['city']} vs {city2_profile['city']} 宜居度对比",
        polar=dict(radialaxis=dict(visible=True, range=[0, 100]))
    )
    return fig.to_html()

#3.仪表盘图
def make_gauge(city_name, score):
    """
    Generate a beautiful gauge chart for a city's livability score
    """
    import plotly.graph_objects as go
    
    # 根据分数设置颜色主题
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
            'font': {'size': 36, 'color': title_color}
        },
        number={
            'font': {'size': 48, 'color': bar_color},
            'suffix': " pts"
        },
        gauge={
            'axis': {
                'range': [0, 100],
                'tickwidth': 2,
                'tickcolor': "#34495e",
                'tickfont': {'size': 12}
            },
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
    
    fig.update_layout(
        height=400,
        width=500,
        paper_bgcolor="#f8f9fa"
    )
    return fig.to_html()

if __name__ == '__main__':              #用于测试的数据
    from data_fetcher import get_city_profile
    
    # 测试 Tokyo
    tokyo = get_city_profile('Tokyo')
    score = calculate_score(tokyo)
    print(f"Tokyo 评分: {score}")
    
    # 生成仪表盘图
    gauge_html = make_gauge('Tokyo', score)
    with open('gauge_Tokyo.html', 'w', encoding='utf-8') as f:
        f.write(gauge_html)
    print("仪表盘图已生成: gauge_Tokyo.html")