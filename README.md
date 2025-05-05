# WhatsApp Chat Analyzer Dashboard 📱

This project is a **Streamlit-based web application** that allows you to analyze WhatsApp chat exports. The app performs sentiment analysis, visualizes messaging trends, and assesses breakup risk based on message patterns.

---

## 🔑 Key Features

- 📈 **Messages per Sender**: Visualize the frequency of messages sent by each participant.
- 🧠 **Sentiment Analysis**: Analyze and categorize messages as Positive, Negative, or Neutral.
- 📊 **Sentiment Trend Over Time**: Track sentiment fluctuations throughout the conversation timeline.
- 💔 **Breakup Risk Assessment**: Calculates a risk score based on message patterns, sentiment, and response time.
- 🔍 **Interactive Dashboard**: Filter and analyze chat messages with an easy-to-use interface.
- 📂 **Exportable Data**: View detailed message logs with timestamps and sentiment.

---

## 🧰 Technologies Used

- **Python 3.x**
- **Streamlit** for creating the interactive dashboard
- **TextBlob** for sentiment analysis
- **Pandas** for data processing and manipulation
- **Matplotlib & Seaborn** for data visualization
- **Regex** for parsing WhatsApp chat logs

---

## ⚙️ Local Development Setup

### 📋 Prerequisites

- Python 3.10 or later
- pip (Python package manager)

### 🧪 Run Locally

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/whatsapp_dashboard.git
cd whatsapp_dashboard

# 2. Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install project dependencies
pip install -r requirements.txt

# 4. Run the Streamlit app
streamlit run whatsapp_dashboard.py
```

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/kamble0805/whatsapp-chat-analyzer/blob/main/MIT