"""PPC Performance Dashboard - Streamlit application.

Run with: streamlit run app.py
"""
from __future__ import annotations

import io
import os

import pandas as pd
import plotly.express as px
import streamlit as st

from data_processor import (
    aggregate_by,
    compare_periods,
    filter_dataframe,
    normalize_dataframe,
    summarize,
)

st.set_page_config(page_title="PPC Performance Dashboard", page_icon="📈", layout="wide")
st.title("PPC Performance Dashboard")
st.caption(
    "Upload a Google Ads / Meta Ads / Bing Ads export (CSV or XLSX) with a date column and "
    "campaign/ad group dimensions. The dashboard normalizes columns, computes KPIs, filters, "
    "and compares periods automatically."
)

SAMPLE_PATH = os.path.join(os.path.dirname(__file__), "sample_data.csv")

source = st.radio("Data source", ["Upload a file", "Use bundled sample data"], horizontal=True)

df_raw = None
if source == "Upload a file":
    uploaded = st.file_uploader("Upload campaign export", type=["csv", "xlsx"])
    if uploaded is not None:
        if uploaded.name.lower().endswith(".xlsx"):
            df_raw = pd.read_excel(uploaded)
        else:
            df_raw = pd.read_csv(uploaded)
else:
    if os.path.exists(SAMPLE_PATH):
        df_raw = pd.read_csv(SAMPLE_PATH)

if df_raw is None:
    st.info("Please upload a file or choose sample data to continue.")
    st.stop()

try:
    df = normalize_dataframe(df_raw)
except ValueError as exc:
    st.error(f"Could not normalize the file: {exc}")
    st.stop()

st.success(f"Loaded {len(df):,} rows. Date range: {df['date'].min().date()} to {df['date'].max().date()}")

campaigns = sorted(df["campaign"].dropna().unique().tolist())
ad_groups = sorted(df["ad_group"].dropna().unique().tolist())
min_date = df["date"].min().date()
max_date = df["date"].max().date()

with st.sidebar:
    st.header("Filters")
    start_date = st.date_input("Start date", min_date, min_value=min_date, max_value=max_date)
    end_date = st.date_input("End date", max_date, min_value=min_date, max_value=max_date)
    if start_date > end_date:
        st.error("Start date must be before end date.")
        st.stop()
    selected_campaigns = st.multiselect("Campaigns", campaigns, default=campaigns)
    selected_groups = st.multiselect("Ad groups", ad_groups, default=ad_groups)

filtered = filter_dataframe(df, start_date, end_date, selected_campaigns, selected_groups)
summary = summarize(filtered)

c1, c2, c3, c4, c5, c6, c7, c8 = st.columns(8)
c1.metric("Impressions", f"{summary.impressions:,}")
c2.metric("Clicks", f"{summary.clicks:,}")
c3.metric("Spend", f"${summary.spend:,.2f}")
c4.metric("Conversions", f"{summary.conversions:,}")
c5.metric("CTR", f"{summary.ctr:.2f}%")
c6.metric("CPC", f"${summary.cpc:.2f}")
c7.metric("Cost/Conv.", f"${summary.cpa:.2f}")
c8.metric("Conv. rate", f"{summary.conversion_rate:.2f}%")

st.subheader("Trend")
daily = aggregate_by(filtered, "date")
fig = px.line(
    daily,
    x="date",
    y=["clicks", "conversions"],
    labels={"value": "Count", "variable": "Metric", "date": "Date"},
    title="Clicks and conversions over time",
)
st.plotly_chart(fig, use_container_width=True)

st.subheader("Performance by campaign")
by_campaign = aggregate_by(filtered, "campaign")
fig2 = px.bar(
    by_campaign,
    x="campaign",
    y=["impressions", "clicks"],
    barmode="group",
    labels={"value": "Count", "variable": "Metric", "campaign": "Campaign"},
    title="Impressions and clicks by campaign",
)
st.plotly_chart(fig2, use_container_width=True)
st.dataframe(by_campaign, use_container_width=True, hide_index=True)

st.subheader("Performance by ad group")
by_group = aggregate_by(filtered, "ad_group")
st.dataframe(by_group, use_container_width=True, hide_index=True)

st.subheader("Period comparison")
period_days = (end_date - start_date).days + 1
prev_end = start_date - pd.Timedelta(days=1)
prev_start = prev_end - pd.Timedelta(days=period_days - 1)
current = filter_dataframe(df, start_date, end_date, selected_campaigns, selected_groups)
previous = filter_dataframe(df, prev_start.date(), prev_end.date(), selected_campaigns, selected_groups)
comparison = compare_periods(current, previous)
st.caption(f"Comparing {start_date} to {end_date} against {prev_start.date()} to {prev_end.date()}")
st.dataframe(comparison, use_container_width=True, hide_index=True)

csv_buffer = io.StringIO()
by_campaign.to_csv(csv_buffer, index=False)
st.download_button("Download campaign summary CSV", data=csv_buffer.getvalue(), file_name="campaign_summary.csv", mime="text/csv")
