import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import time
import requests

# --- CONFIG ---
st.set_page_config(page_title="Global Energy Terminal 2026", layout="wide")

country = "India"
daily_volume = 5000000

st.title(f"🌍 {country} Energy Desk | 2026 Live")

# -------------------------
# CACHED DATA FUNCTIONS
# -------------------------

@st.cache_data(ttl=60)
def get_oil_prices():
    tickers = ['BZ=F', 'CL=F']
    try:
        data = yf.download(
            tickers,
            period="5d",
            interval="5m",
            group_by='ticker',
            progress=False
        )
        return data.ffill()
    except:
        return pd.DataFrame()


@st.cache_data(ttl=120)
def get_gas_prices():
    tickers = ['NG=F', 'JKM=F', 'TTF=F', 'EURUSD=X']
    try:
        data = yf.download(
            tickers,
            period="5d",
            interval="15m",
            group_by='ticker',
            progress=False
        )
        return data.ffill()
    except:
        return pd.DataFrame()


# -------------------------
# FETCH OIL DATA
# -------------------------

oil_data = get_oil_prices()

if oil_data.empty:
    st.error("Oil price data could not be loaded.")
    st.stop()

brent_series = oil_data['BZ=F']['Close'].dropna() if 'BZ=F' in oil_data else pd.Series()
wti_series = oil_data['CL=F']['Close'].dropna() if 'CL=F' in oil_data else pd.Series()

# -------------------------
# FETCH GAS DATA
# -------------------------

gas_data = get_gas_prices()

ng_series = gas_data['NG=F']['Close'].dropna() if 'NG=F' in gas_data else pd.Series()
jkm_series = gas_data['JKM=F']['Close'].dropna() if 'JKM=F' in gas_data else pd.Series()
ttf_series = gas_data['TTF=F']['Close'].dropna() if 'TTF=F' in gas_data else pd.Series()
eurusd_series = gas_data['EURUSD=X']['Close'].dropna() if 'EURUSD=X' in gas_data else pd.Series()

# Convert TTF (EUR/MWh) → USD/MMBtu
if not ttf_series.empty and not eurusd_series.empty:
    ttf_usd_mmbtu = (ttf_series * eurusd_series) / 3.412
else:
    ttf_usd_mmbtu = pd.Series()

# -------------------------
# SAFE PRICE EXTRACTION
# -------------------------

brent_price = brent_series.iloc[-1] if not brent_series.empty else 0
wti_price = wti_series.iloc[-1] if not wti_series.empty else 0
ng_price = ng_series.iloc[-1] if not ng_series.empty else 0
jkm_price = jkm_series.iloc[-1] if not jkm_series.empty else 0
ttf_price = ttf_usd_mmbtu.iloc[-1] if not ttf_usd_mmbtu.empty else 0

# -------------------------
# TOP METRICS
# -------------------------

m1, m2, m3, m4, m5, m6 = st.columns(6)

m1.metric("Brent (ICE)", f"${brent_price:.2f}")
m2.metric("WTI (NYMEX)", f"${wti_price:.2f}")
m3.metric("NYMEX NG", f"${ng_price:.2f}/MMBtu")
m4.metric("JKM LNG", f"${jkm_price:.2f}/MMBtu")
m5.metric("TTF (USD adj)", f"${ttf_price:.2f}/MMBtu")
m6.metric("Last Sync", datetime.now().strftime("%H:%M:%S"))

st.markdown("---")

# -------------------------
# OIL CHART
# -------------------------

fig_oil = go.Figure()

if not brent_series.empty:
    fig_oil.add_trace(go.Scatter(
        x=brent_series.index,
        y=brent_series,
        name="Brent",
        line=dict(color='#00CC96', width=2)
    ))

if not wti_series.empty:
    fig_oil.add_trace(go.Scatter(
        x=wti_series.index,
        y=wti_series,
        name="WTI",
        line=dict(color='#EF553B', width=2, dash='dot')
    ))

fig_oil.update_layout(
    title="Crude Oil Price Comparison",
    template="plotly_dark",
    height=450,
    hovermode="x unified"
)

st.plotly_chart(fig_oil, use_container_width=True)

# -------------------------
# GAS CHART
# -------------------------

st.markdown("### 🔥 Global Natural Gas Benchmarks (USD/MMBtu)")

fig_gas = go.Figure()

if not ng_series.empty:
    fig_gas.add_trace(go.Scatter(
        x=ng_series.index,
        y=ng_series,
        name="NYMEX NG",
        line=dict(width=2)
    ))

if not jkm_series.empty:
    fig_gas.add_trace(go.Scatter(
        x=jkm_series.index,
        y=jkm_series,
        name="JKM LNG",
        line=dict(width=2)
    ))

if not ttf_usd_mmbtu.empty:
    fig_gas.add_trace(go.Scatter(
        x=ttf_usd_mmbtu.index,
        y=ttf_usd_mmbtu,
        name="TTF (USD adj)",
        line=dict(width=2)
    ))

fig_gas.update_layout(
    template="plotly_dark",
    height=450,
    hovermode="x unified"
)

st.plotly_chart(fig_gas, use_container_width=True)

# -------------------------
# SPREADS
# -------------------------

spread1 = jkm_price - ng_price
spread2 = ttf_price - ng_price

s1, s2 = st.columns(2)

s1.metric("JKM – NG Spread", f"${spread1:.2f}")
s2.metric("TTF – NG Spread", f"${spread2:.2f}")

# -------------------------
# FINANCIAL IMPACT
# -------------------------

st.markdown("### 💰 Oil Financial Impact Analysis")

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

csv_data = impact_df.to_csv(index=False).encode('utf-8')

st.download_button(
    label="📥 Download Impact Report (CSV)",
    data=csv_data,
    file_name=f"energy_report_{datetime.now().strftime('%Y%m%d')}.csv",
    mime="text/csv"
)

time.sleep(30)
st.rerun()
