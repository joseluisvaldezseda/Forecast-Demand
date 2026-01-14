import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# ==========================================
# 1. PAGE CONFIGURATION & STYLING
# ==========================================
st.set_page_config(
    page_title="S&OP Control Tower",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional CSS: Minimalist, clean font, tight spacing
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .block-container {padding-top: 1rem; padding-bottom: 2rem;}
    div[data-testid="stMetricValue"] {font-size: 1.5rem; font-weight: 600;}
    h1, h2, h3 {font-family: 'Segoe UI', sans-serif; font-weight: 400;}
    .stSelectbox label {font-weight: bold;}
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. DATA LOADING & CACHING
# ==========================================
@st.cache_data
def load_data():
    # Load Backtesting (Historical)
    df_b = pd.read_parquet("demo_backtesting_data.parquet")
    df_b['date'] = pd.to_datetime(df_b['date'])
    
    # Load Future Forecast
    df_f = pd.read_parquet("demo_forecast_data.parquet")
    df_f['date'] = pd.to_datetime(df_f['date'])
    
    return df_b, df_f

try:
    df_back, df_pred = load_data()
except FileNotFoundError:
    st.error("Data files not found. Please ensure .parquet files are generated.")
    st.stop()

# ==========================================
# 3. METRICS ENGINE
# ==========================================
def calculate_metrics(df):
    if df.empty: return 0, 0, 0
    
    y_true = df['qty_sold']
    y_pred = df['qty_forecast']
    total_actual = y_true.sum()
    
    if total_actual == 0: return 0, 0, 0

    # WMAPE: Weighted Mean Absolute Percentage Error
    wmape = (np.abs(y_true - y_pred).sum() / total_actual) * 100
    
    # Bias: (Forecast - Actual) / Actual. 
    # Positive = Overforecast (High Inventory Risk). Negative = Underforecast (Lost Sales Risk).
    bias = ((y_pred - y_true).sum() / total_actual) * 100
    
    # Forecast Accuracy
    accuracy = max(0, 100 - wmape)
    
    return wmape, bias, accuracy

# ==========================================
# 4. ADVANCED SIDEBAR FILTERS (FULL HIERARCHY)
# ==========================================
st.sidebar.header("Business Hierarchy Filters")

# 1. Date Range (Global)
min_date, max_date = df_back['date'].min(), df_pred['date'].max()
dates = st.sidebar.date_input("Analysis Period", [min_date, max_date], min_value=min_date, max_value=max_date)

# 2. Store Format (Business Unit)
formats = ["All Formats"] + sorted(df_back['store_format'].unique().tolist())
sel_format = st.sidebar.selectbox("1. Store Format", formats)

# Filter Level 1
df_l1 = df_back[df_back['store_format'] == sel_format] if sel_format != "All Formats" else df_back

# 3. Product Group (Replacement for Department)
groups = ["All Groups"] + sorted(df_l1['product_group'].unique().tolist())
sel_group = st.sidebar.selectbox("2. Product Group", groups)

# Filter Level 2
df_l2 = df_l1[df_l1['product_group'] == sel_group] if sel_group != "All Groups" else df_l1

# 4. Brand (New Layer)
brands = ["All Brands"] + sorted(df_l2['brand'].unique().tolist())
sel_brand = st.sidebar.selectbox("3. Brand", brands)

# Filter Level 3
df_l3 = df_l2[df_l2['brand'] == sel_brand] if sel_brand != "All Brands" else df_l2

# 5. Demand Profile (Strategic Segmentation)
profiles = ["All Profiles"] + sorted(df_l3['demand_profile'].unique().tolist())
sel_profile = st.sidebar.selectbox("4. Demand Profile", profiles)

# Filter Level 4
df_l4 = df_l3[df_l3['demand_profile'] == sel_profile] if sel_profile != "All Profiles" else df_l3

# 6. SKU Selection
skus = ["All SKUs"] + sorted(df_l4['sku_id'].unique().tolist())
sel_sku = st.sidebar.selectbox("5. Select Specific SKU", skus)

# --- APPLY FINAL FILTERS FUNCTION ---
def apply_filters(df):
    mask_date = (df['date'] >= pd.to_datetime(dates[0])) & (df['date'] <= pd.to_datetime(dates[1]))
    d = df.loc[mask_date]
    if sel_format != "All Formats": d = d[d['store_format'] == sel_format]
    if sel_group != "All Groups": d = d[d['product_group'] == sel_group]
    if sel_brand != "All Brands": d = d[d['brand'] == sel_brand]
    if sel_profile != "All Profiles": d = d[d['demand_profile'] == sel_profile]
    if sel_sku != "All SKUs": d = d[d['sku_id'] == sel_sku]
    return d

df_b_final = apply_filters(df_back)
df_f_final = apply_filters(df_pred)

# ==========================================
# 5. MAIN DASHBOARD UI
# ==========================================
st.title("S&OP Control Tower")
st.markdown(f"**Context:** {sel_format} > {sel_group} > {sel_brand}")

# --- ROW 1: EXECUTIVE KPIs ---
wmape, bias, acc = calculate_metrics(df_b_final)
sales = df_b_final['sales_amount'].sum()
avg_inv = df_b_final['inventory_qty'].mean()

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("Revenue (Period)", f"${sales:,.0f}")
col2.metric("Forecast Accuracy", f"{acc:.1f}%", help="100% - WMAPE")
col3.metric("Global WMAPE", f"{wmape:.1f}%", delta="-2%" if wmape < 25 else "2%", delta_color="inverse", help="Weighted Mean Absolute Percentage Error")
col4.metric("Forecast Bias", f"{bias:.1f}%", help="Positive=Overforecast, Negative=Underforecast")
col5.metric("Avg Inventory", f"{avg_inv:,.0f} units")

st.markdown("---")

# ==========================================
# 6. STRATEGIC TABS
# ==========================================
tab1, tab2, tab3 = st.tabs(["Strategic Overview", "End-to-End Planning", "SKU Deep Dive"])

# --- TAB 1: STRATEGIC OVERVIEW ---
with tab1:
    c1, c2 = st.columns([2, 1])
    
    with c1:
        st.subheader("Historical Demand vs Forecast")
        # Aggregation by Date
        agg_ts = df_b_final.groupby('date')[['qty_sold', 'qty_forecast']].sum().reset_index()
        
        fig_ts = go.Figure()
        fig_ts.add_trace(go.Scatter(x=agg_ts['date'], y=agg_ts['qty_sold'], name='Actual Sales', 
                                    line=dict(color='#2C3E50', width=2)))
        fig_ts.add_trace(go.Scatter(x=agg_ts['date'], y=agg_ts['qty_forecast'], name='Forecast', 
                                    line=dict(color='#E74C3C', width=2, dash='dot')))
        
        fig_ts.update_layout(template="plotly_white", margin=dict(t=10, b=10), hovermode="x unified", 
                             legend=dict(orientation="h", y=1.1))
        st.plotly_chart(fig_ts, use_container_width=True)
        
    with c2:
        st.subheader("Accuracy by Profile")
        if sel_profile == "All Profiles":
            grp_prof = df_b_final.groupby('demand_profile').apply(
                lambda x: calculate_metrics(x)[0]
            ).reset_index(name='WMAPE').sort_values('WMAPE')
            
            fig_bar = px.bar(grp_prof, x='WMAPE', y='demand_profile', orientation='h', 
                             color='WMAPE', color_continuous_scale='RdYlGn_r', text='WMAPE')
            fig_bar.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
            fig_bar.update_layout(template="plotly_white", xaxis_title="WMAPE % (Lower is Better)")
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("Select 'All Profiles' to see comparative breakdown.")
            
    # Product Group Performance
    st.subheader("Performance by Product Group")
    if sel_group == "All Groups":
        grp_metrics = df_b_final.groupby('product_group').agg(
            Sales=('sales_amount', 'sum'),
            Profit=('gross_profit', 'sum')
        ).reset_index()
        
        fig_tree = px.bar(grp_metrics, x='Sales', y='product_group', orientation='h', 
                          color='Profit', title="Revenue & Profit Contribution by Group")
        fig_tree.update_layout(template="plotly_white")
        st.plotly_chart(fig_tree, use_container_width=True)

# --- TAB 2: END-TO-END PLANNING (HYBRID VIEW) ---
with tab2:
    st.subheader("Supply Chain Projection")
    
    # 1. Prepare Historical Data
    hist_agg = df_b_final.groupby('date')[['qty_sold', 'inventory_qty']].sum().reset_index()
    
    # 2. Prepare Future Data
    fut_agg = df_f_final.groupby('date')[['qty_forecast', 'inventory_qty']].sum().reset_index()
    
    fig_full = go.Figure()
    
    # A. Historical Inventory (Dark Grey)
    fig_full.add_trace(go.Bar(
        x=hist_agg['date'], y=hist_agg['inventory_qty'], 
        name='Hist. Inventory', marker_color='#7F8C8D', opacity=0.5
    ))
    
    # B. Future Inventory (Light Grey)
    fig_full.add_trace(go.Bar(
        x=fut_agg['date'], y=fut_agg['inventory_qty'], 
        name='Proj. Inventory', marker_color='#BDC3C7', opacity=0.5
    ))
    
    # C. Actual Sales (Dark Line)
    fig_full.add_trace(go.Scatter(
        x=hist_agg['date'], y=hist_agg['qty_sold'], 
        name='Actual Sales', line=dict(color='#2C3E50', width=2)
    ))
    
    # D. Future Forecast (Blue Line)
    fig_full.add_trace(go.Scatter(
        x=fut_agg['date'], y=fut_agg['qty_forecast'], 
        name='Forecast Demand', line=dict(color='#2980B9', width=2)
    ))
    
    # Visual Separator "Today"
    last_hist_date = hist_agg['date'].max()
    if pd.notna(last_hist_date):
        fig_full.add_vline(x=last_hist_date, line_width=1, line_dash="dash", line_color="black")
        fig_full.add_annotation(x=last_hist_date, y=hist_agg['qty_sold'].max(), text="Today", showarrow=False, yshift=10)
    
    fig_full.update_layout(
        template="plotly_white", 
        barmode='overlay', 
        hovermode="x unified",
        legend=dict(orientation="h", y=1.1),
        yaxis_title="Units",
        height=500
    )
    st.plotly_chart(fig_full, use_container_width=True)
    
    st.markdown("### Projection Summary by Brand")
    summary = df_f_final.groupby(['product_group', 'brand'])[['qty_forecast', 'inventory_qty']].sum().reset_index()
    st.dataframe(summary.style.format("{:,.0f}", subset=['qty_forecast', 'inventory_qty']), use_container_width=True)

# --- TAB 3: SKU DEEP DIVE ---
with tab3:
    if sel_sku == "All SKUs":
        st.markdown("### Watchlist: High Error / High Value SKUs")
        
        # Logic: Find High Value + High Error items
        sku_ranking = df_b_final.groupby(['sku_id', 'product_group', 'brand', 'demand_profile']).agg(
            Total_Sales=('sales_amount', 'sum'),
            Total_Forecast=('qty_forecast', 'sum'),
            Total_Actual=('qty_sold', 'sum')
        ).reset_index()
        
        # Calculate WMAPE per row
        sku_ranking['Abs_Error'] = abs(sku_ranking['Total_Actual'] - sku_ranking['Total_Forecast'])
        sku_ranking['WMAPE'] = (sku_ranking['Abs_Error'] / sku_ranking['Total_Actual']) * 100
        sku_ranking['Bias'] = ((sku_ranking['Total_Forecast'] - sku_ranking['Total_Actual']) / sku_ranking['Total_Actual']) * 100
        
        # Filter: Only show items with sales
        sku_ranking = sku_ranking[sku_ranking['Total_Sales'] > 0]
        
        # Top 15 sorted by Sales Amount
        top_skus = sku_ranking.sort_values('Total_Sales', ascending=False).head(15)
        
        st.dataframe(
            top_skus[['sku_id', 'product_group', 'brand', 'demand_profile', 'Total_Sales', 'WMAPE', 'Bias']]
            .style.format({'Total_Sales': '${:,.0f}', 'WMAPE': '{:.1f}%', 'Bias': '{:.1f}%'})
            .background_gradient(subset=['WMAPE'], cmap='Reds'),
            use_container_width=True
        )
        
    else:
        st.markdown(f"### Product 360: {sel_sku}")
        
        # METADATA CARDS
        # Get metadata from the first row of the selection
        meta = df_back[df_back['sku_id'] == sel_sku].iloc[0]
        
        m1, m2, m3, m4 = st.columns(4)
        m1.info(f"**Format:** {meta['store_format']}")
        m2.info(f"**Group:** {meta['product_group']}")
        m3.info(f"**Brand:** {meta['brand']}")
        m4.info(f"**Profile:** {meta['demand_profile']}")
        
        # SKU Specific Metrics
        s_wmape, s_bias, s_acc = calculate_metrics(df_b_final)
        
        k1, k2, k3 = st.columns(3)
        k1.metric("SKU Accuracy", f"{s_acc:.1f}%")
        k2.metric("SKU Bias", f"{s_bias:.1f}%")
        k3.metric("Total Sales", f"${df_b_final['sales_amount'].sum():,.0f}")
        
        # UNIFIED CHART (History + Future)
        fig_master = go.Figure()
        
        # 1. Historical Actuals
        fig_master.add_trace(go.Scatter(
            x=df_b_final['date'], y=df_b_final['qty_sold'], 
            name='Actual Sales', line=dict(color='black', width=2)
        ))
        
        # 2. Historical Forecast (Show error)
        fig_master.add_trace(go.Scatter(
            x=df_b_final['date'], y=df_b_final['qty_forecast'], 
            name='Hist. Forecast', line=dict(color='red', width=1, dash='dot')
        ))
        
        # 3. Future Forecast
        fig_master.add_trace(go.Scatter(
            x=df_f_final['date'], y=df_f_final['qty_forecast'], 
            name='Future Forecast', line=dict(color='green', width=2)
        ))
        
        # 4. Integrated Inventory
        # Combine dates and inventory for a smooth area chart
        combined_dates = pd.concat([df_b_final['date'], df_f_final['date']])
        combined_inv = pd.concat([df_b_final['inventory_qty'], df_f_final['inventory_qty']])
        
        fig_master.add_trace(go.Scatter(
            x=combined_dates, y=combined_inv,
            name='Inventory Level', fill='tozeroy', 
            line=dict(color='lightgrey', width=0), opacity=0.2
        ))
        
        fig_master.update_layout(
            title="End-to-End Product Lifecycle",
            template="plotly_white",
            hovermode="x unified",
            xaxis_title="Timeline",
            yaxis_title="Units"
        )
        
        # Add a vertical line for "Today"
        split_date = df_b_final['date'].max()
        fig_master.add_vline(x=split_date, line_width=1, line_dash="dash", line_color="grey")
        

        st.plotly_chart(fig_master, use_container_width=True)

