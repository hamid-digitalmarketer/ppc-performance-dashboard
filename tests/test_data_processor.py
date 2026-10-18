"""Unit tests for the PPC dashboard data processor."""

import pandas as pd
import pytest

from data_processor import (
    aggregate_by,
    compare_periods,
    filter_dataframe,
    normalize_dataframe,
    summarize,
)


@pytest.fixture
def df():
    return pd.DataFrame(
        {
            "Date": ["2025-01-01", "2025-01-01", "2025-01-02", "2025-01-02"],
            "Campaign": ["Search - Brand", "Search - Generic", "Search - Brand", "Search - Generic"],
            "Impressions": [1000, 2000, 1500, 2500],
            "Clicks": [50, 60, 40, 80],
            "Spend": [25.0, 30.0, 20.0, 40.0],
            "Conversions": [3, 2, 1, 4],
        }
    )


def test_normalize_lowercases_columns_and_parses_date(df):
    norm = normalize_dataframe(df)
    assert "campaign" in norm.columns
    assert "date" in norm.columns
    assert pd.api.types.is_datetime64_any_dtype(norm["date"])
    assert norm["spend"].dtype.kind == "f"


def test_summarize_computes_totals(df):
    norm = normalize_dataframe(df)
    s = summarize(norm)
    assert s.impressions == 7000
    assert s.clicks == 230
    assert s.spend == 115.0
    assert s.conversions == 10
    assert round(s.ctr, 2) == round(230 / 7000 * 100, 2)
    assert round(s.cpc, 2) == round(115 / 230, 2)
    assert round(s.cpa, 2) == round(115 / 10, 2)


def test_filter_by_campaign(df):
    norm = normalize_dataframe(df)
    filtered = filter_dataframe(norm, campaigns=["Search - Brand"])
    assert set(filtered["campaign"].unique()) == {"Search - Brand"}
    assert filtered["clicks"].sum() == 90


def test_filter_by_date_range(df):
    norm = normalize_dataframe(df)
    filtered = filter_dataframe(norm, start_date="2025-01-02", end_date="2025-01-02")
    assert filtered["date"].nunique() == 1


def test_aggregate_by_campaign(df):
    norm = normalize_dataframe(df)
    agg = aggregate_by(norm, "campaign")
    assert set(agg["campaign"]) == {"Search - Brand", "Search - Generic"}
    brand = agg[agg["campaign"] == "Search - Brand"].iloc[0]
    assert brand["clicks"] == 90
    assert brand["impressions"] == 2500


def test_compare_periods(df):
    norm = normalize_dataframe(df)
    current = norm[norm["date"] == pd.Timestamp("2025-01-02")]
    previous = norm[norm["date"] == pd.Timestamp("2025-01-01")]
    comp = compare_periods(current, previous)
    assert "Change (%)" in comp.columns
    row = comp[comp["KPI"] == "Clicks"].iloc[0]
    assert row["Current"] == 120
    assert row["Previous"] == 110
