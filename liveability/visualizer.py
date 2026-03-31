from .data_fetcher import get_city_profile, get_city_history
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# ===== 1. 宜居度评分 =====
def calculate_score(city_profile):
    static = city_profile['static_data']
    live = city_profile['live_data']
    
    safety = static.get('safety_index', 50)
    health = static.get('health_index', 50)
    cost = static.get('cost_of_living', 50)
    property_ratio = static.get('property_ratio', 50)
    traffic_time = static.get('traffic_time', 50)
    pollution = static.get('pollution_index', 50)
    climate = static.get('climate_index', 50)
    
    temp = live['temp']
    aqi = live['aqi']
    
    if temp is None:
        temp = 20
    if 20 <= temp <= 25:
        temp_score = 100
    else:
        temp_score = 100 - min(abs(temp - 22.5) * 5, 100)
    
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
    
    cost_score = max(0, 100 - cost)
    property_score = max(0, 100 - property_ratio)
    traffic_score = max(0, 100 - traffic_time)
    pollution_score = max(0, 100 - pollution)
    climate_score = climate
    
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
    categories = ['温度', '空气质量', '安全指数', '医疗指数', '生活成本', 
                  '房价收入比', '通勤时间', '污染指数', '气候指数']
    
    static1 = city1_profile['static_data']
    live1 = city1_profile['live_data']
    
    city1_values = [
        live1['temp'],
        100 - live1['aqi'],
        static1.get('safety_index', 50),
        static1.get('health_index', 50),
        100 - static1.get('cost_of_living', 50),
        100 - static1.get('property_ratio', 50),
        100 - static1.get('traffic_time', 50),
        100 - static1.get('pollution_index', 50),
        static1.get('climate_index', 50)
    ]
    
    static2 = city2_profile['static_data']
    live2 = city2_profile['live_data']
    
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
        title=f"{city1_profile['city']} vs {city2_profile['city']} Livability Comparison",
        title_font_size=20,
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100], gridcolor='#e9ecef'),
            angularaxis=dict(tickfont=dict(size=10)),
            bgcolor='#f8f9fa'
        ),
        paper_bgcolor='#f8f9fa',
        height=500,
        showlegend=True,
        legend=dict(x=0.9, y=1.1)
    )
    return fig.to_html(full_html=False, include_plotlyjs='cdn')


# ===== 3. 仪表盘图 =====
def make_gauge(city_name, score):
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
            'font': {'size': 18, 'color': bar_color},
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
    
    fig.update_layout(height=350, paper_bgcolor="#f8f9fa")
    return fig.to_html(full_html=False, include_plotlyjs='cdn')


# ===== 4. 趋势图 =====
def make_trend_chart(city_name, city_history):
    if city_history['status'] != 'success':
        return "<p>Unable to get historical data</p>"
    
    years_data = city_history['years_data']
    
    data = []
    for item in years_data:
        temp_profile = {
            'static_data': {
                'safety_index': item.get('safety_index', 50),
                'health_index': item.get('health_index', 50),
                'cost_of_living': item.get('cost_of_living', 50),
                'property_ratio': item.get('property_ratio', 50),
                'traffic_time': item.get('traffic_time', 50),
                'pollution_index': item.get('pollution_index', 50),
                'climate_index': item.get('climate_index', 50)
            },
            'live_data': {
                'temp': 20,
                'aqi': 50
            }
        }
        score = calculate_score(temp_profile)
        data.append({'year': item['year'], 'score': score})
    
    df = pd.DataFrame(data)
    df = df.sort_values('year')
    
    fig = px.line(
        df, 
        x='year', 
        y='score',
        title=f'{city_name} Livability Trend',
        markers=True,
        line_shape='linear'
    )
    
    fig.update_traces(
        line=dict(color='#4C72B0', width=3),
        marker=dict(size=8, color='#DD8452')
    )
    
    fig.update_layout(
        xaxis_title='Year',
        yaxis_title='Livability Score',
        yaxis_range=[0, 100],
        hovermode='x',
        plot_bgcolor='#f8f9fa',
        paper_bgcolor='#f8f9fa',
        height=400,
        font=dict(family="Arial", size=12)
    )
    
    fig.add_hline(y=70, line_dash="dash", line_color="green", 
                  annotation_text="Excellent (70+)", annotation_position="top right")
    fig.add_hline(y=50, line_dash="dash", line_color="#C44E52",
                  annotation_text="Pass (50+)", annotation_position="bottom right")
    
    return fig.to_html(full_html=False, include_plotlyjs='cdn')


if __name__ == '__main__':
    from data_fetcher import get_city_profile, get_city_history
    
    tokyo = get_city_profile('Tokyo')
    score = calculate_score(tokyo)
    print(f"东京评分: {score}")
    
    gauge_html = make_gauge('Tokyo', score)
    with open('gauge_tokyo.html', 'w', encoding='utf-8') as f:
        f.write(gauge_html)
    print("仪表盘图已生成: gauge_tokyo.html")
    
    london = get_city_profile('London')
    radar_html = make_radar(tokyo, london)
    with open('radar_tokyo_london.html', 'w', encoding='utf-8') as f:
        f.write(radar_html)
    print("雷达图已生成: radar_tokyo_london.html")
    
    london_history = get_city_history('London')
    trend_html = make_trend_chart('London', london_history)
    with open('trend_london.html', 'w', encoding='utf-8') as f:
        f.write(trend_html)
    print("趋势图已生成: trend_london.html")