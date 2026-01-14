# S&OP Control Tower: Demand Forecasting & Inventory Management

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://forecast-demand-retail.streamlit.app/)

A professional Sales & Operations Planning dashboard for retail demand forecasting and inventory optimization, powered by advanced time series models and interactive analytics.

## Overview

Enterprise-grade forecasting system covering **22,201 SKUs** across multiple product categories, store formats, and demand profiles. The application combines historical backtesting (2022-2024) with forward-looking projections for 2025.

**Core Capabilities:**
- Multi-level business hierarchy filtering (Store Format → Product Group → Brand → SKU)
- Demand segmentation with specialized model allocation
- Real-time accuracy metrics (WMAPE, Bias, Correlation)
- End-to-end supply chain visualization
- SKU-level performance diagnostics

---

## Data Architecture

### Input Files
- `demo_backtesting_data.parquet` – Historical sales and forecast performance (2022-2024)
- `demo_forecast_data.parquet` – 12-month forward projections (2025)

### Schema
```
date             | datetime64[ns]
sku_id           | object
store_format     | object  [Discount Warehouse, Premium Dept. Store]
product_group    | object  [Electronics, Home & Living, Apparel, Sports, Beauty, Toys, Automotive]
brand            | object  [Brand_01 to Brand_24]
demand_profile   | object  [New - Volatile, Growth - Volatile, Mature - Intermittent, etc.]
qty_forecast     | int64
inventory_qty    | int64
qty_sold         | int64   (backtesting only)
sales_amount     | float64 (backtesting only)
gross_profit     | float64 (backtesting only)
```

---

## Forecasting Models

The system employs five specialized models based on product lifecycle and demand characteristics:

| Demand Profile | Model | MAE | RMSE | Bias % | MAPE | Correlation | SKU Count |
|---|---|---:|---:|---:|---:|---:|---:|
| **Mature - Volatile**<br><sub>≥24 meses, <40% zeros, CV >10%</sub> | ARIMA Seasonal<br><sub>(auto_arima, iterative forecast)</sub> | 8.45 | 11.21 | 0.85 | 8.5 | 0.925 | 6,909 |
| **Growth - Volatile**<br><sub>≥12 & <23 meses, <40% zeros, CV >10%</sub> | Prophet<br><sub>(no daily/weekly seasonality)</sub> | 12.15 | 16.89 | -1.20 | 11.2 | 0.845 | 5,084 |
| **Mature - Intermittent**<br><sub>≥12 meses, >40% zeros, CV <10%</sub> | ARIMA Non-Seasonal | 4.23 | 6.54 | 1.95 | 14.6 | 0.680 | 3,270 |
| **New - Volatile**<br><sub><12 meses, <40% zeros, CV >10%</sub> | ARIMA Non-Seasonal | 18.75 | 24.12 | -2.80 | 21.4 | 0.550 | 4,226 |
| **New - Low Volume**<br><sub><12 meses, >40% zeros, CV <10%</sub> | XGBoost / Moving Average | 6.11 | 8.45 | 1.50 | 12.8 | 0.720 | 2,712 |

### Model Implementation Details

**1. Seasonal ARIMA (Mature Products)**
```python
auto_arima(
    serie, seasonal=True, m=12, D=1,
    max_p=5, max_q=5, max_P=2, max_Q=2,
    stepwise=True, method='lbfgs'
)
# Iterative 12-month forecast with 0.95 reduction factor
```

**2. Prophet (Growth Phase)**
```python
Prophet(
    daily_seasonality=False,
    weekly_seasonality=False,
    yearly_seasonality=True
)
```

**3. Non-Seasonal ARIMA (New/Intermittent)**
```python
auto_arima(
    serie, seasonal=False,
    max_p=5, max_q=5, max_d=2,
    information_criterion='aic'
)
```

**4. XGBoost Regressor (Low Volume)**
```python
XGBRegressor(
    n_estimators=300, learning_rate=0.05,
    max_depth=3, subsample=0.8
)
# Features: time index, month, year
```

---

## Application Features

### 1. Strategic Overview
- Time series visualization (Actual vs Forecast)
- Accuracy breakdown by demand profile
- Revenue and profit contribution by product group

### 2. End-to-End Planning
- Integrated historical and projected timeline
- Inventory coverage visualization
- Brand-level projection summaries

### 3. SKU Deep Dive
- High-value/high-error watchlist
- Product lifecycle analysis
- Metadata cards (format, group, brand, profile)
- Unified historical + future view

### Key Performance Metrics
- **WMAPE** (Weighted Mean Absolute Percentage Error)
- **Forecast Bias** (Over/Under forecast indicator)
- **Accuracy** (100% - WMAPE)
- **Revenue & Profitability** tracking

---

## Installation & Usage

### Prerequisites
```bash
Python 3.9+
```

### Dependencies
```bash
streamlit
pandas
plotly
numpy
pyarrow
```

### Local Deployment
```bash
# Clone repository
git clone https://github.com/joseluisvaldezseda/forecast-demand-retail.git
cd forecast-demand-retail

# Install requirements
pip install -r requirements.txt

# Run application
streamlit run app.py
```

### Data Preprocessing
```bash
# Generate demo datasets (requires source parquets)
python data_preparation.py
```

---

## Project Structure

```
├── app.py                          # Main Streamlit dashboard
├── data_preparation.py             # ETL pipeline for demo data generation
├── Generate_Forecast.yxmd          # Alteryx workflow (forecasting engine)
├── Models_Used.ipynb               # Model documentation & validation
├── demo_backtesting_data.parquet   # Historical dataset
├── demo_forecast_data.parquet      # Future projections
└── requirements.txt                # Python dependencies
```

---

## Technical Specifications

**Framework:** Streamlit 1.x  
**Visualization:** Plotly 5.x  
**Data Storage:** Apache Parquet (columnar format)  
**Forecasting Engine:** pmdarima, Prophet, XGBoost  
**Parallel Processing:** joblib (multi-core execution)  

**Performance:**
- Dataset size: 22,201 SKUs × 36 months = ~800K records
- Dashboard load time: <2s (cached)
- Model execution: Parallelized across all CPU cores

---

## Metrics Glossary

**WMAPE:** Weighted Mean Absolute Percentage Error – Industry-standard accuracy metric weighted by sales volume  
**Bias:** Systematic forecast error indicating over/under prediction tendency  
**CV:** Coefficient of Variation – Demand volatility indicator  
**Correlation:** Pearson correlation between actual and forecasted values

---

## License

MIT License - See LICENSE file for details

---

## Author

**Jose Luis Valdez Seda**  
[GitHub](https://github.com/joseluisvaldezseda) | [LinkedIn](https://linkedin.com/in/joseluisvaldezseda)

---

## Live Demo

🔗 **[Launch Application](https://forecast-demand-retail.streamlit.app/)**

*For enterprise deployment or custom model development, contact the author.*s
