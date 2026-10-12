# PPC Performance Dashboard

An interactive paid-media performance dashboard built with Python, Pandas, Plotly, and Streamlit. Upload a Google Ads / Meta Ads / Bing Ads export, and get normalized KPIs, filters, trend charts, campaign and ad group breakdowns, period-over-period comparison, and CSV export — all in one page.

## Problem it solves

Marketers waste hours stitching CSV exports into Excel to answer simple questions: *"How did CTR change this month?"*, *"Which ad group has the lowest cost per conversion?"* This dashboard answers those questions instantly with consistent KPI definitions (CTR, CPC, CPA, conversion rate) and honest, clearly-labeled derived metrics.

## Key features

- Upload CSV or XLSX exports; column names are normalized automatically (date, campaign, ad group, impressions, clicks, spend, conversions)
- Automatic KPI calculation: CTR, CPC, Cost/Conversion, conversion rate
- Sidebar filters: date range, campaign, ad group
- Trend chart for clicks and conversions over time
- Performance tables and charts by campaign and by ad group
- Period-over-period comparison with absolute and percentage deltas
- Download summarized results as CSV
- Bundled synthetic sample data for an instant demo

## Data expectations

The dashboard expects at least a date column and one or more of: impressions, clicks, spend, conversions. Recognized date column names include `date`, `day`, `Date`. Campaign and ad group columns are optional but recommended. Any numeric column that is missing is treated as zero; derived metrics are never invented — they are computed from the columns actually present.

## Technology stack

- Python 3.11
- Pandas (data processing)
- Plotly (interactive charts)
- Streamlit (web UI)
- openpyxl (XLSX upload support)

## Folder structure

```
ppc-performance-dashboard/
├── app.py                  # Streamlit application
├── data_processor.py       # Normalization, KPI, filter, aggregation, comparison engine
├── tests/
│   └── test_data_processor.py
├── sample_data.csv         # Synthetic demo data (8 weeks, 4 campaigns)
├── requirements.txt
└── .gitignore
```

## Installation

```bash
python -m venv venv
# Windows: venv\Scripts\activate  |  macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
```

## Usage

```bash
streamlit run app.py
```

Choose **Use bundled sample data** for an instant demo, or upload your own campaign export.

## Testing

```bash
pytest -q
```

Tests cover column normalization, KPI math, campaign filters, date-range filters, aggregation, and period comparison.

## Limitations and known issues

- The comparison assumes calendar-aligned equal-length periods
- Real exports vary by ad platform; unknown columns are ignored (no guessing)
- No multi-touch attribution or incrementality modeling — the dashboard reports platform-reported metrics as-is

## Future improvements

- Budget pacing / burn-rate alerts
- Multi-platform data merge (Google Ads + Meta + Bing)
- Forecasts using simple time-series models
- Scheduled email delivery of the report

## License

MIT (add a `LICENSE` file before commercial use if required by your use case).

---

**Developed by Muhammad Hamid**

Digital Marketing | SEO | Performance Marketing | E-commerce | Web Development

- Portfolio: [https://abouthamid.web.app/](https://abouthamid.web.app/)
- LinkedIn: [https://www.linkedin.com/in/muhammad-hamid-digital-marketing/](https://www.linkedin.com/in/muhammad-hamid-digital-marketing/)
- WhatsApp: [https://wa.me/923167417135](https://wa.me/923167417135)

Have a project, job opportunity, or collaboration in mind? [Contact Muhammad Hamid on WhatsApp](https://wa.me/923167417135).
