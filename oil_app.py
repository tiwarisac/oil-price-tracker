import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import time
import requests

# --- CONFIG ---
st.set_page_config(page_title="Global Oil Terminal 2026", layout="wide")

# --- DATA FUNCTIONS ---
def get_oil_prices():
    # Multi-ticker download returns a MultiIndex DataFrame
    tickers = ['BZ=F', 'CL=F']
    data = yf.download(tickers, period="5d", interval="1m", group_by='ticker', progress=False)
    return data.ffill()

def get_real_eia_data(api_key):
    if not api_key:
        return pd.DataFrame({"Week": ["Feb 27"], "Stocks (M)": [851.2], "Change": [+1.9]})
    try:
        url = f"https://api.eia.gov/v2/petroleum/stoc/wstk/data/?api_key={api_key}&frequency=weekly&data[0]=value&facets[series][]=WCESTUS1&sort[0][column]=period&sort[0][direction]=desc&length=5"
        response = requests.get(url).json()
        df = pd.DataFrame(response['response']['data'])
        return df[['period', 'value']].rename(columns={'period': 'Week', 'value': 'Stocks (M)'})
    except:
        return pd.DataFrame()

# --- SIDEBAR ---
st.sidebar.title("Terminal Settings")
EIA_API_KEY = st.sidebar.text_input("EIA API Key", type="password")
country = st.sidebar.selectbox("Importer", ["India", "China", "Germany", "USA"])
volumes = {"India": 5000000, "China": 11000000, "Germany": 2000000, "USA": 6000000}
daily_volume = st.sidebar.number_input("Daily Barrels", value=volumes[country])
alert_threshold = st.sidebar.slider("Brent Alert ($)", 60, 100, 78)

# --- MAIN INTERFACE ---
st.title(f"🛢️ {country} Energy Desk | 2026 Live")

# Fetch data
raw_data = get_oil_prices()
brent_series = raw_data['BZ=F']['Close'].dropna()
wti_series = raw_data['CL=F']['Close'].dropna()

if not brent_series.empty and not wti_series.empty:
    brent_price = brent_series.iloc[-1]
    wti_price = wti_series.iloc[-1]
    
    # 1. TOP METRICS
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Brent (ICE)", f"${brent_price:.2f}")
    m2.metric("WTI (NYMEX)", f"${wti_price:.2f}")
    m3.metric("Daily BPS Cost", f"${(daily_volume * brent_price * 0.0001):,.2f}")
    m4.metric("Last Sync", datetime.now().strftime("%H:%M:%S"))

    st.markdown("---")

    # 2. MIDDLE SECTION (Live Chart & Inventory)
    col_chart, col_inv = st.columns([3, 1])
    
    with col_chart:
        fig = go.Figure()
        # Brent Line
        fig.add_trace(go.Scatter(x=brent_series.index, y=brent_series, name="Brent (Global)", line=dict(color='#00CC96', width=2)))
        # WTI Line (Fixed)
        fig.add_trace(go.Scatter(x=wti_series.index, y=wti_series, name="WTI (US)", line=dict(color='#EF553B', width=2, dash='dot')))
        
        fig.update_layout(title="Crude Oil Price Comparison", template="plotly_dark", height=450, hovermode="x unified")
        st.plotly_chart(fig, use_container_width=True)

    with col_inv:
        st.subheader("EIA Inventory Hub")
        st.dataframe(get_real_eia_data(EIA_API_KEY), hide_index=True)
        st.caption("Data: US Commercial Crude Stocks")

    # 3. BOTTOM SECTION (Impact Table & Download)
    st.markdown("### 💰 Financial Impact Analysis")
    
    impact_df = pd.DataFrame({
        "Scenario": ["+10 BPS Move", "+100 BPS Move", "+$1.00 Rise"],
        "Daily Cost Increase": [
            f"${(daily_volume * brent_price * 0.001):,.2f}", 
            f"${(daily_volume * brent_price * 0.01):,.2f}", 
            f"${daily_volume:,.2f}"
        ],
        "Market Implication": ["Marginal", "Significant", "Major Shift"]
    })
    
    st.table(impact_df)
    
    # DOWNLOAD BUTTON (Fixed Key)
    csv_data = impact_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Impact Report (CSV)",
        data=csv_data,
        file_name=f"oil_report_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
        key="main_download_btn" # Now safe outside the while loop
    )

    # REFRESH LOGIC
    time.sleep(30)
    st.rerun() # This is the "Streamlit Way" to refresh the page safely