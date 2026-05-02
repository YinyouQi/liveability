# Global City Liveability Intelligence & Forecast Platform

A full-stack data intelligence SaaS platform designed to eliminate information asymmetry in global relocation. It integrates real-time environmental APIs, historical infrastructure data, and Scikit-Learn predictive models to provide precise city retrieval, dynamic rankings, and 2027 liveability forecasting.

## 🛠 Tech Stack
- **Backend:** Python, Django MVT Architecture, SQLite
- **Frontend:** HTML5/CSS3, JavaScript, Bootstrap (Responsive UI)
- **Data & ML:** Pandas, Scikit-Learn (Polynomial & Linear Regression)
- **Visualization:** Plotly (Interactive Radar & Gauge Charts)

## ✨ Core Features
* **Real-time Synchronization:** Dynamically fetches weather and AQI for 300+ global cities via OpenWeatherMap and AQICN APIs.
* **4-Layer High Availability API Mechanism:** Implements Cache (30min TTL), Rate Limiting (1 req/sec), Error Retry, and Mock Fallback to ensure page rendering never freezes.
* **Predictive Trend Analysis:** Leverages historical time-series data (2020-2026) to project 2027 liveability indicators.
* **High-Density Dashboard:** Harmonizes heterogeneous data sources into interactive dual-city comparative reports with an automated AI Insight Summary engine.

## ⚙️ System Architecture Highlights
* **Controller (`views.py`):** Reconstructed the core controller to inject multi-source API data into the frontend rendering context.
* **Fuzzy Retrieval:** Robust search engine with 3-level keyword fuzzy matching (Exact -> Contains -> Simplified).
* **Data Persistence:** User authentication framework and "Favorites" system utilizing Django ORM (`unique_together` constraints).

## 🚀 Quick Start

1. Clone the repository and install dependencies:
```bash
git clone https://github.com/YinyouQi/liveability.git
cd liveability
pip install django pandas scikit-learn plotly requests

Apply database migrations:
code
Bash
python manage.py makemigrations
python manage.py migrate
Start the server:
code
Bash
python manage.py runserver
Visit http://127.0.0.1:8000 to access the platform.
