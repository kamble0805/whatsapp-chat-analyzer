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

# Function to find occurrences of breakup-related terms in messages
def count_breakup_terms(message, breakup_terms):
    message = message.lower()
    return sum([term in message for term in breakup_terms])

# Function to find occurrences of "sorry"-related terms in messages
def count_sorry_terms(message, sorry_terms):
    message = message.lower()
    return sum([term in message for term in sorry_terms])

# Breakup risk assessment function
def breakup_risk_assessment(df):
    # Factor 1: Breakup-related term count
    breakup_count = df['Breakup_Count'].sum()
    
    # Factor 2: Negative sentiment distribution
    negative_sentiment = df[df['Sentiment'] == 'Negative'].shape[0]
    
    # Factor 3: Messages per sender (if one sender dominates the conversation)
    sender_counts = df['Sender'].value_counts(normalize=True) * 100
    dominant_sender_percentage = sender_counts.max()
    
    # Factor 4: Average response time (in minutes)
    avg_response_time = df['TimeDiff'].mean()

    # Calculate breakup risk score (simple weighted score based on the factors)
    risk_score = 0

    if breakup_count > 5:
        risk_score += 25  # Increase score for higher breakup-related term usage
    if negative_sentiment > 0.3 * len(df):  # If more than 30% of messages are negative sentiment
        risk_score += 30
    if dominant_sender_percentage > 65:  # If one sender dominates more than 65% of messages
        risk_score += 20
    if avg_response_time > 45:  # If the average response time is more than 45 minutes
        risk_score += 15

    # Determine the risk level
    if risk_score >= 70:
        risk_level = "🔴 High Risk"
    elif risk_score >= 40:
        risk_level = "🟠 Moderate Risk"
    else:
        risk_level = "🟢 Low Risk"

    return risk_score, risk_level

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
            # Define breakup-related terms and sorry-related terms
            breakup_terms = ['breakup', 'broken up', 'end this', 'splitting up', 'break-up', 'part ways', 'split up']
            sorry_terms = [
                'sorry', 'apologies', 'sorry about that', 'my bad', 'excuse me', 'pardon me', 
                'i apologize', 'regret', 'forgive me'
            ]

            # Count occurrences of breakup and sorry terms per message
            df['Breakup_Count'] = df['Message'].apply(lambda x: count_breakup_terms(x, breakup_terms))
            df['Sorry_Count'] = df['Message'].apply(lambda x: count_sorry_terms(x, sorry_terms))

            # Get total breakup and sorry term counts per sender
            breakup_counts_per_sender = df.groupby('Sender')['Breakup_Count'].sum()
            sorry_counts_per_sender = df.groupby('Sender')['Sorry_Count'].sum()

            st.header("💔 Breakup Term Usage by Sender")
            st.write(breakup_counts_per_sender)

            st.header("🙏 'Sorry' Term Usage by Sender")
            st.write(sorry_counts_per_sender)

            # Sentiment analysis and time difference
            df['Sentiment'] = df['Message'].apply(analyze_sentiment)
            df['TimeDiff'] = df['Timestamp'].diff().dt.total_seconds() / 60

            # Breakup risk assessment
            risk_score, risk_level = breakup_risk_assessment(df)
            st.header("🧪 Breakup Risk Assessment")
            st.metric("Breakup Risk Score", f"{risk_score} / 100", risk_level)

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

            st.header("📂 Full Message Table")
            st.dataframe(df[['Timestamp', 'Sender', 'Message', 'Sentiment']])
    except Exception as e:
        st.error(f"Failed to process the chat file: {e}")
else:
    st.info("Please upload a WhatsApp .txt chat export to begin.")
