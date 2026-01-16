from collections import Counter
import re

def generate_nlp_summary(news_df):
    if news_df.empty:
        return "No significant competitor activity detected."

    text = " ".join(news_df["Title"].tolist()).lower()

    keywords = re.findall(r"\b[a-z]{4,}\b", text)
    keyword_counts = Counter(keywords)

    focus_terms = [
        "defense", "government", "contract",
        "launch", "satellite", "partnership",
        "acquisition", "funding"
    ]

    insights = []
    for term in focus_terms:
        if keyword_counts[term] > 0:
            insights.append(f"• Increased activity around **{term}**")

    top_company = news_df["Company"].value_counts().idxmax()

    summary = f"""
**Executive Market Summary**
- {top_company} is the most active competitor
- {len(news_df)} relevant news articles identified
{chr(10).join(insights)}
    """

    return summary.strip()
