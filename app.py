import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import base64

from collections import defaultdict

from scripts.fetch_news import fetch_news
from scripts.fetch_stock import (
    fetch_stock_data,
    compute_sentiment,
    compute_average_market_trend
)
from scripts.competitors import COMPETITORS
from scripts.email_alerts import send_email_alert


# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="Competitive Intelligence Command Center",
    layout="wide"
)

st.markdown("""
<style>

/* ===== GLOBAL BACKGROUND ===== */
.stApp {
    background:
        linear-gradient(
            rgba(3, 7, 18, 0.85),
            rgba(3, 7, 18, 0.85)
        ),
        url("https://images.unsplash.com/photo-1446776811953-b23d57bd21aa?auto=format&fit=crop&w=2000&q=80");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
    font-family: 'Inter', sans-serif;
}
/* -------- LOGO -------- */
.logo-container {
    display: flex;
    align-items: center;
    gap: 14px;
}

.logo-container img {
    height: 42px;
    width: auto;
}

/* ===== CONTENT WIDTH ===== */
.block-container {
    max-width: 1400px;
    padding: 2.5rem 3rem;
}

/* ===== HERO ===== */
.hero {
    background: linear-gradient(
        135deg,
        rgba(15, 23, 42, 0.88),
        rgba(30, 41, 59, 0.88)
    );
    padding: 2.5rem 3rem;
    border-radius: 22px;
    box-shadow: 0 20px 50px rgba(0,0,0,0.45);
    margin-bottom: 3rem;
    border: 1px solid rgba(148,163,184,0.2);
}

/* ===== HERO TEXT ===== */
.hero-title {
    color: #e0f2fe;
    font-weight: 800;
    letter-spacing: 0.5px;
}

.hero-subtitle {
    color: #c7d2fe;
    font-size: 1.05rem;
}

/* ===== CARDS ===== */
.card {
    background: rgba(15, 23, 42, 0.78);
    backdrop-filter: blur(12px);
    padding: 2rem;
    border-radius: 20px;
    box-shadow: 0 18px 45px rgba(0,0,0,0.45);
    margin-bottom: 2.5rem;
    border: 1px solid rgba(148,163,184,0.18);
}

/* ===== HEADINGS (VISIBLE FIX) ===== */
h1, h2, h3 {
    color: #e5e7eb !important;
    font-weight: 700;
}

p, li, span, small {
    color: #cbd5f5 !important;
}

/* ===== SIDEBAR ===== */
section[data-testid="stSidebar"] {
    background: linear-gradient(
        180deg,
        rgba(15, 23, 42, 0.98),
        rgba(2, 6, 23, 0.98)
    );
    border-right: 1px solid rgba(148,163,184,0.2);
}

/* ===== SIDEBAR LABELS ===== */
section[data-testid="stSidebar"] label {
    color: #e0f2fe !important;
    font-weight: 600;
}

/* ===== DROPDOWNS ===== */
section[data-testid="stSidebar"] div[data-baseweb="select"] > div {
    background-color: rgba(15,23,42,0.9) !important;
    border: 1px solid rgba(148,163,184,0.35);
    color: #f8fafc !important;
    border-radius: 10px;
}

/* ===== SECTION FOOTER ===== */
.section-footer {
    margin-top: 1rem;
    font-size: 0.8rem;
    color: #94a3b8;
    border-top: 1px solid rgba(148,163,184,0.2);
    padding-top: 0.75rem;
}

</style>
""", unsafe_allow_html=True)


# ================= HERO =================
st.markdown(
    """
    <div class="logo-container">
        <img src="data:image/png;base64,{}">
        <h1>Competitive Intelligence Command Center</h1>
    </div>
    <p class="hero-subtitle">
        Monitor competitor activity, market trends, and analyst sentiment — all in one place.
    </p>
    """.format(
        base64.b64encode(
            open("assets/xdlinx_logo.png", "rb").read()
        ).decode()
    ),
    unsafe_allow_html=True
)

st.markdown("</div>", unsafe_allow_html=True)


# ================= SIDEBAR =================
st.sidebar.header("Filters")

all_regions = sorted({v["region"] for v in COMPETITORS.values()})
all_categories = sorted({v["category"] for v in COMPETITORS.values()})

selected_regions = st.sidebar.multiselect("Region", all_regions)
selected_categories = st.sidebar.multiselect("Category", all_categories)

display_name_map = {
    f"{name} ({meta['category']})": name
    for name, meta in COMPETITORS.items()
}

filtered_display = [
    d for d, actual in display_name_map.items()
    if (not selected_regions or COMPETITORS[actual]["region"] in selected_regions)
    and (not selected_categories or COMPETITORS[actual]["category"] in selected_categories)
]

selected_display = st.sidebar.multiselect(
    "Search & select competitors",
    filtered_display
)

competitors = [display_name_map[d] for d in selected_display][:2]

date_range = st.sidebar.selectbox(
    "Date Range",
    ["Last 7 days", "Last 30 days", "Last 90 days"],
    index=1
)






# ================= DATA PREP =================
news_df = fetch_news(competitors) if competitors else pd.DataFrame()

alert_news = (
    news_df[news_df["priority_score"] >= 2].copy()
    if not news_df.empty and "priority_score" in news_df.columns
    else pd.DataFrame()
)

def classify_alert(score):
    return "High" if score >= 3 else "Medium"

if not alert_news.empty:
    alert_news["alert_level"] = alert_news["priority_score"].apply(classify_alert)

    # ================= EXECUTIVE INTELLIGENCE SUMMARY =================

st.subheader("Executive Intelligence Summary")

if competitors and not news_df.empty:
    top_company = news_df["Company"].value_counts().idxmax()
    top_mentions = news_df["Company"].value_counts().max()

    high_alert_count = (
        alert_news[alert_news["alert_level"] == "High"].shape[0]
        if not alert_news.empty and "alert_level" in alert_news.columns
        else 0
    )

    summary_lines = [
        f"Selected competitors show sustained strategic and market-facing activity during the selected period.",
        f"{top_company} leads overall media and analyst attention with {top_mentions} reported developments.",
    ]

    if high_alert_count > 0:
        summary_lines.append(
            f"{high_alert_count} high-priority developments were detected, indicating potential near-term operational or market impact."
        )

    summary_lines.append(
        "Overall activity patterns suggest increased competitive intensity and justify continued monitoring."
    )

    for line in summary_lines:
        st.markdown(f"- {line}")

else:
    st.info("Select competitors to generate an executive-level intelligence summary.")

st.markdown(
    "<div class='section-footer'>"
    "This summary is automatically generated from aggregated news signals, alert severity, "
    "and competitor activity patterns."
    "</div>",
    unsafe_allow_html=True
)

st.markdown("</div>", unsafe_allow_html=True)


# ================= ALERT CENTER =================
st.subheader("🚨 Alert Center")

if alert_news.empty:
    st.info("No high-priority alerts detected.")
else:
    for _, row in alert_news.head(5).iterrows():
        if row["alert_level"] == "High":
            st.error(f"🔥 {row['Company']}: {row['Title']}")
        else:
            st.warning(f"⚠️ {row['Company']}: {row['Title']}")

st.markdown(
    "<div class='section-footer'>Alerts generated using keyword intensity and relevance scoring.</div>",
    unsafe_allow_html=True
)
st.markdown("</div>", unsafe_allow_html=True)


# ================= NEWS =================

st.subheader("Competitor News")

priority = news_df[news_df["priority_score"] > 0] if not news_df.empty else pd.DataFrame()
other = news_df[news_df["priority_score"] == 0] if not news_df.empty else pd.DataFrame()

if not priority.empty:
    st.markdown("### 🔥 Priority News")
    for _, row in priority.iterrows():
        st.markdown(
            f"• **{row['Company']}** — "
            f"<a href='{row['Link']}' target='_blank'>{row['Title']}</a><br>"
            f"<small>{row['Published']}</small>",
            unsafe_allow_html=True
        )

if not other.empty:
    st.markdown("### 📰 Other News")
    for _, row in other.iterrows():
        st.markdown(
            f"• **{row['Company']}** — "
            f"<a href='{row['Link']}' target='_blank'>{row['Title']}</a><br>"
            f"<small>{row['Published']}</small>",
            unsafe_allow_html=True
        )

st.markdown(
    "<div class='section-footer'>Click any headline to open the original source.</div>",
    unsafe_allow_html=True
)
st.markdown("</div>", unsafe_allow_html=True)


# ================= MARKET SNAPSHOT =================

st.subheader("Market Snapshot")

if not news_df.empty:
    top = news_df["Company"].value_counts().idxmax()
    count = news_df["Company"].value_counts().max()
    st.markdown(f"""
- **{top}** leads with **{count} media mentions**
- Sustained competitive and investor activity detected
- High-impact contracts and partnerships emerging
""")

st.markdown(
    "<div class='section-footer'>Auto-generated from news volume and alert intensity.</div>",
    unsafe_allow_html=True
)
st.markdown("</div>", unsafe_allow_html=True)


# ================= STOCK TRENDS =================

st.subheader("Market & Stock Trends")

mode = st.radio(
    "View Mode",
    ["Company Comparison", "Region Comparison"],
    horizontal=True
)

if mode == "Company Comparison":
    fig = go.Figure()
    dfs = []

    for c in competitors:
        hist, _ = fetch_stock_data(c)
        if not hist.empty:
            dfs.append(hist)
            fig.add_trace(go.Scatter(
                x=hist.index,
                y=hist["Close"],
                name=c,
                mode="lines"
            ))

    avg = compute_average_market_trend(dfs)
    if not avg.empty:
        fig.add_trace(go.Scatter(
            x=avg.index,
            y=avg,
            name="Market Average",
            mode="lines",
            line=dict(dash="dash", width=3)
        ))

    st.plotly_chart(fig, use_container_width=True)

else:
    region_map = defaultdict(list)

    for name, meta in COMPETITORS.items():
        if meta["type"] == "public":
            hist, _ = fetch_stock_data(name)
            if not hist.empty:
                region_map[meta["region"]].append(hist)

    fig = go.Figure()
    for region, dfs in region_map.items():
        avg = compute_average_market_trend(dfs)
        if not avg.empty:
            fig.add_trace(go.Scatter(
                x=avg.index,
                y=avg,
                name=region,
                mode="lines"
            ))

    st.plotly_chart(fig, use_container_width=True)

    # ================= INDIVIDUAL COMPETITOR GRAPHS =================
if competitors:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("Individual Competitor Performance")

    for company in competitors:
        meta = COMPETITORS.get(company)

        # Handle private companies safely
        if meta["type"] != "public":
            st.info(f"{company} is a private company. Stock data not available.")
            continue

        hist, _ = fetch_stock_data(company)

        if hist.empty:
            st.warning(f"No stock data available for {company}.")
            continue

        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=hist.index,
                y=hist["Close"],
                mode="lines",
                name=company,
                line=dict(width=3, color="#38bdf8")
            )
        )

        fig.update_layout(
            title=f"{company} — Individual Stock Trend",
            xaxis_title="Date",
            yaxis_title="Price (USD)",
            template="plotly_white",
            height=360,
            margin=dict(l=40, r=40, t=60, b=40)
        )

        st.plotly_chart(fig, use_container_width=True)

    st.markdown(
        "<div class='section-footer'>"
        "Individual charts enable focused, competitor-level performance analysis "
        "independent of peer comparison."
        "</div>",
        unsafe_allow_html=True
    )

    st.markdown("</div>", unsafe_allow_html=True)


st.markdown(
    "<div class='section-footer'>Stock data sourced from Yahoo Finance.</div>",
    unsafe_allow_html=True
)
st.markdown("</div>", unsafe_allow_html=True)


# ================= FOOTER =================
st.markdown("---")
st.caption("Competitive Intelligence Command Center • Internal Use Only")

def generate_executive_summary(news_df, alert_news, competitors):
    if not competitors:
        return "No competitors selected. Please select competitors to generate insights."

    summary = []

    summary.append(
        f"The competitive landscape analysis currently focuses on "
        f"{', '.join(competitors)}."
    )

    if not news_df.empty:
        top_company = news_df["Company"].value_counts().idxmax()
        mentions = news_df["Company"].value_counts().max()

        summary.append(
            f"{top_company} is the most active competitor, accounting for "
            f"{mentions} recent media mentions."
        )

    if not alert_news.empty:
        high_alerts = alert_news[alert_news["alert_level"] == "High"]

        if not high_alerts.empty:
            summary.append(
                "Several high-impact developments were detected, including "
                "contracts, partnerships, or government-related activities."
            )
        else:
            summary.append(
                "Moderate-impact developments suggest ongoing strategic activity "
                "without immediate disruption."
            )

    keywords = ["defense", "government", "contract", "launch", "satellite"]
    keyword_hits = news_df["Title"].str.lower().str.contains(
        "|".join(keywords), na=False
    ).sum()

    if keyword_hits > 0:
        summary.append(
            "Thematic analysis indicates increased focus on defense, government, "
            "and satellite-related initiatives."
        )

    summary.append(
        "Overall, market signals point to sustained competitive momentum, "
        "with selective high-impact events worth executive attention."
    )

    return " ".join(summary)




