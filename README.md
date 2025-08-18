# 🛒 Demand Forecasting for La Marina & El Bodegón (Colima)

## Project Overview
Demand forecasting is the practice of using historical sales data, statistical models, and machine learning techniques to estimate future product demand.  
For retailers like **La Marina** and **El Bodegón** in Colima, accurate demand forecasts are essential to:
- Ensure the right products are available at the right time  
- Minimize stockouts  
- Reduce overstock  
- Optimize supply chain operations  

This repository contains the code, data pipelines, and models developed to build a robust demand forecasting solution tailored for the retail sector in Colima.

---

## Methodology
1. **Data Collection & Preprocessing**  
   - Historical sales data from different departments, product groups, and brands.  
   - Cleaning, aggregation, and transformation into time series.  

2. **Exploratory Data Analysis (EDA)**  
   - Identifying sales patterns, seasonality, and outliers.  
   - Visualizations for product categories and demand trends.  

3. **Modeling Approaches**  
   - Statistical models: ARIMA, SARIMA  
   - Machine learning models: XGBoost, Random Forest, Ridge Regression  
   - Deep learning: Prophet, LSTM (optional for long-term sequences)  

4. **Evaluation Metrics**  
   - Mean Absolute Error (MAE)  
   - Root Mean Squared Error (RMSE)  
   - Mean Absolute Percentage Error (MAPE)  

5. **Forecasting & Deployment**  
   - Weekly demand predictions at the brand & product-group level.  
   - Results exported in CSV and visualized in interactive dashboards.  

---

## 📊 Results
- Forecast accuracy improved by combining classical models with ML techniques.  
- Granular forecasts (per brand/product group) allow better **inventory planning** and **strategic purchasing**.  
- Helps reduce excess inventory costs while preventing product shortages.  

---

## Future Work
- Incorporate **external factors** (holidays, promotions, inflation).  
- Improve accuracy with **hybrid models** (Prophet + XGBoost).  
- Deploy API for **real-time forecasting**.  

---

## 📂 Repository Structure
├── data/ # Raw and processed datasets
├── notebooks/ # Jupyter/Colab notebooks with analysis & models
├── models/ # Trained forecasting models
├── results/ # Forecast outputs and evaluation metrics
├── requirements.txt # Dependencies
└── README.md # Project documentation


---

## 👨‍💻 Author
**José Luis Valdéz Seda**  
Data Scientist | Retail Analytics | Forecasting & Machine Learning  
