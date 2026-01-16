import feedparser
import pandas as pd
import time

IMPORTANT_KEYWORDS = [
    "contract", "deal", "launch", "acquisition",
    "partnership", "award", "funding",
    "government", "military", "defense"
]

COMPETITOR_RSS = {
    "Planet Labs": "https://news.google.com/rss/search?q=Planet+Labs",
    "Spire Global": "https://news.google.com/rss/search?q=Spire+Global",
    "BlackSky": "https://news.google.com/rss/search?q=BlackSky"
    # add more as needed
}


def score_news(title: str) -> int:
    title_lower = title.lower()
    return sum(1 for word in IMPORTANT_KEYWORDS if word in title_lower)


def classify_alert(score: int) -> str:
    if score >= 3:
        return "High"
    elif score == 2:
        return "Medium"
    else:
        return "Low"


def fetch_news(selected_competitors, max_items=5):
    rows = []

    for company in selected_competitors:
        feed_url = COMPETITOR_RSS.get(company)
        if not feed_url:
            continue

        try:
            feed = feedparser.parse(
                feed_url,
                agent="Mozilla/5.0 (CompetitiveIntelligenceDashboard/1.0)"
            )

            for entry in feed.entries[:max_items]:
                title = entry.get("title", "")

                rows.append({
                    "Company": company,
                    "Title": title,
                    "Published": entry.get("published", ""),
                    "Link": entry.get("link", ""),
                    "priority_score": score_news(title)
                })

            # Small delay to reduce rate limiting
            time.sleep(0.3)

        except Exception:
            continue

    news_df = pd.DataFrame(rows)

    if news_df.empty:
        return news_df

    # ✅ ALERT LEVEL CALCULATION BELONGS HERE
    news_df["alert_level"] = news_df["priority_score"].apply(classify_alert)

    news_df = news_df.sort_values(
        by=["priority_score", "Published"],
        ascending=[False, False]
    )

    return news_df

