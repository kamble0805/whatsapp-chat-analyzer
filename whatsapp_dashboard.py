import pandas as pd
import re
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
from textblob import TextBlob

# Load chat from uploaded file-like object
def load_chat(uploaded_file):
    lines = uploaded_file.read().decode('utf-8').splitlines()
    messages = []
    pattern = r'^(\d{1,2}/\d{1,2}/\d{2,4}),\s(\d{1,2}:\d{2}(?:\s?[APap][Mm])?)\s-\s(.*?):\s(.*)'

    for line in lines:
        match = re.match(pattern, line)
        if match:
            date, time, sender, message = match.groups()
            datetime_str = f"{date} {time}"
            try:
                timestamp = pd.to_datetime(datetime_str, dayfirst=True)
                messages.append([timestamp, sender, message])
            except:
                continue

    df = pd.DataFrame(messages, columns=['Timestamp', 'Sender', 'Message'])
    return df

# Sentiment analysis
def analyze_sentiment(text):
    polarity = TextBlob(text).sentiment.polarity
    if polarity > 0.1:
        return 'Positive'
    elif polarity < -0.1:
        return 'Negative'
    else:
        return 'Neutral'

# Breakup likelihood scoring
def breakup_likelihood(df):
    sender_counts = df['Sender'].value_counts(normalize=True) * 100
    score = 0
    if sender_counts.max() > 65:
        score += 25

    sentiment_distribution = df['Sentiment'].value_counts(normalize=True) * 100
    if sentiment_distribution.get('Negative', 0) > 30:
        score += 30

    response_times = df.groupby('Sender')['TimeDiff'].mean()
    if response_times.max() > 45:
        score += 20

    avg_len = df['Message'].apply(len).groupby(df['Sender']).mean()
    if avg_len.min() < 20:
        score += 15

    if score >= 70:
        risk = "🔴 High Risk"
    elif score >= 40:
        risk = "🟠 Moderate Risk"
    else:
        risk = "🟢 Low Risk"
    return score, risk

# ========== Streamlit App ==========

st.set_page_config(page_title="WhatsApp Chat Analyzer", layout="wide")
st.title("📱 WhatsApp Relationship Dashboard")

uploaded_file = st.file_uploader("Upload exported WhatsApp chat (.txt file)", type="txt")

if uploaded_file:
    try:
        df = load_chat(uploaded_file)
        if df.empty:
            st.warning("No valid messages were parsed. Check if the file format matches expected WhatsApp export.")
        else:
            df['Sentiment'] = df['Message'].apply(analyze_sentiment)
            df['TimeDiff'] = df['Timestamp'].diff().dt.total_seconds() / 60

            st.header("📊 Overview Statistics")
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("Messages per Sender")
                st.bar_chart(df['Sender'].value_counts())

            with col2:
                st.subheader("Sentiment Distribution")
                st.bar_chart(df['Sentiment'].value_counts())

            st.header("📈 Sentiment Over Time")
            sentiment_trend = df.groupby(df['Timestamp'].dt.date)['Sentiment'].value_counts().unstack().fillna(0)
            st.line_chart(sentiment_trend)

            st.header("🧪 Breakup Risk Assessment")
            score, risk = breakup_likelihood(df)
            st.metric("Breakup Likelihood Score", f"{score} / 100", risk)

            st.header("📂 Full Message Table")
            st.dataframe(df[['Timestamp', 'Sender', 'Message', 'Sentiment']])
    except Exception as e:
        st.error(f"Failed to process the chat file: {e}")
else:
    st.info("Please upload a WhatsApp .txt chat export to begin.")
