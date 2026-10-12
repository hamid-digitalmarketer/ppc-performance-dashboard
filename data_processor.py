"""Data processing engine for the PPC Performance Dashboard.

Loads campaign exports (CSV/XLSX), normalizes column names, computes KPIs,
applies filters, aggregates by dimension, and compares two periods.
"""
from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

DATE_COLUMN_CANDIDATES = ["date", "day", "day_of_week", "Date", "Date range start"]

KPI_COLUMNS = {
    "impressions": "Impressions",
    "clicks": "Clicks",
    "spend": "Spend",
    "conversions": "Conversions",
}

DERIVED_KPIS = {
    "ctr": "CTR (%)",
    "cpc": "CPC",
    "cpa": "Cost / Conversion",
    "conversion_rate": "Conversion rate (%)",
}


@dataclass
class Summary:
    """Totals and derived KPIs for a filtered dataset."""

    impressions: int = 0
    clicks: int = 0
    spend: float = 0.0
    conversions: int = 0

    @property
    def ctr(self) -> float:
        return (self.clicks / self.impressions * 100.0) if self.impressions else 0.0

    @property
    def cpc(self) -> float:
        return (self.spend / self.clicks) if self.clicks else 0.0

    @property
    def cpa(self) -> float:
        return (self.spend / self.conversions) if self.conversions else 0.0

    @property
    def conversion_rate(self) -> float:
        return (self.conversions / self.clicks * 100.0) if self.clicks else 0.0

    def as_dict(self) -> dict:
        return {
            "Impressions": self.impressions,
            "Clicks": self.clicks,
            "Spend": round(self.spend, 2),
            "Conversions": self.conversions,
            "CTR (%)": round(self.ctr, 2),
            "CPC": round(self.cpc, 2),
            "Cost / Conversion": round(self.cpa, 2),
            "Conversion rate (%)": round(self.conversion_rate, 2),
        }


def _coerce_numeric(df: pd.DataFrame) -> pd.DataFrame:
    for col in KPI_COLUMNS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    return df


def normalize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Return a DataFrame with recognized, lower-cased column names."""
    df = df.copy()
    df.columns = [str(c).strip().lower() for c in df.columns]
    df = df.rename(columns={"ad group": "ad_group", "campaign name": "campaign"})
    df = _coerce_numeric(df)

    for candidate in DATE_COLUMN_CANDIDATES:
        if candidate.lower() in df.columns:
            df["date"] = pd.to_datetime(df[candidate.lower()], errors="coerce")
            break
    if "date" not in df.columns:
        raise ValueError("No recognizable date column found (expected 'date', 'day', or similar).")

    for col in KPI_COLUMNS:
        if col not in df.columns:
            df[col] = 0

    if "campaign" not in df.columns:
        df["campaign"] = "All campaigns"
    if "ad_group" not in df.columns:
        df["ad_group"] = "All ad groups"

    return df.dropna(subset=["date"]).sort_values("date").reset_index(drop=True)


def filter_dataframe(df: pd.DataFrame, start_date=None, end_date=None, campaigns=None, ad_groups=None) -> pd.DataFrame:
    """Apply date range, campaign, and ad group filters (inclusive)."""
    result = df.copy()
    if start_date is not None:
        result = result[result["date"] >= pd.Timestamp(start_date)]
    if end_date is not None:
        result = result[result["date"] <= pd.Timestamp(end_date)]
    if campaigns:
        result = result[result["campaign"].isin(campaigns)]
    if ad_groups:
        result = result[result["ad_group"].isin(ad_groups)]
    return result


def summarize(df: pd.DataFrame) -> Summary:
    return Summary(
        impressions=int(df["impressions"].sum()),
        clicks=int(df["clicks"].sum()),
        spend=float(df["spend"].sum()),
        conversions=int(df["conversions"].sum()),
    )


def aggregate_by(df: pd.DataFrame, column: str) -> pd.DataFrame:
    """Aggregate KPIs by a dimension (campaign / ad_group / date)."""
    if column not in df.columns:
        raise ValueError(f"Unknown dimension '{column}'")
    grouped = (
        df.groupby(column, dropna=False)
        .agg(impressions=("impressions", "sum"), clicks=("clicks", "sum"), spend=("spend", "sum"), conversions=("conversions", "sum"))
        .reset_index()
    )
    grouped["ctr"] = grouped.apply(lambda r: (r.clicks / r.impressions * 100) if r.impressions else 0, axis=1)
    grouped["cpc"] = grouped.apply(lambda r: (r.spend / r.clicks) if r.clicks else 0, axis=1)
    grouped["cpa"] = grouped.apply(lambda r: (r.spend / r.conversions) if r.conversions else 0, axis=1)
    grouped["conversion_rate"] = grouped.apply(lambda r: (r.conversions / r.clicks * 100) if r.clicks else 0, axis=1)
    return grouped.sort_values("spend", ascending=False).reset_index(drop=True)


def compare_periods(current: pd.DataFrame, previous: pd.DataFrame) -> pd.DataFrame:
    """Compare KPI totals between two periods with absolute and % deltas."""
    cur = summarize(current).as_dict()
    prev = summarize(previous).as_dict()
    rows = []
    for kpi in cur:
        c = cur[kpi]
        p = prev.get(kpi, 0)
        diff = c - p
        pct = (diff / p * 100) if p else (None if diff == 0 else None)
        rows.append({"KPI": kpi, "Current": c, "Previous": p, "Change": diff, "Change (%)": "" if pct is None else round(pct, 2)})
    return pd.DataFrame(rows)
