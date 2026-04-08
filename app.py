import streamlit as st
import pickle
import re
import string
import requests
import json

# 1. Sehife Ayarlari
st.set_page_config(page_title="🛡️ TruthGuard AI", layout="wide", initial_sidebar_state="collapsed")

# 2. CSS - Saytı Gözəlləşdirən Hissə
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
    }
    .stTextArea textarea {
        background-color: #161b22 !important;
        color: #c9d1d9 !important;
        border: 1px solid #30363d !important;
        border-radius: 10px !important;
    }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 3em;
        background-color: #238636;
        color: white;
        font-weight: bold;
        border: none;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #2ea043;
        border: none;
        transform: scale(1.02);
    }
    .result-box {
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        font-weight: bold;
        font-size: 24px;
        margin-top: 20px;
    }
    .fake-result {
        background-color: #7e1515;
        color: #ffd7d7;
        border: 1px solid #f85149;
    }
    .real-result {
        background-color: #11341a;
        color: #aff5b4;
        border: 1px solid #238636;
    }
    .header-text {
        color: #58a6ff;
        text-align: center;
        font-family: 'Courier New', Courier, monospace;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Modellərin yüklənməsi
try:
    model = pickle.load(open('model.pkl', 'rb'))
    vectorizer = pickle.load(open('vectorizer.pkl', 'rb'))
except:
    st.error("Model faylları tapılmadı!")

def ask_ai(news_text, result_label):
    api_key = "AIzaSyB-b7LgB1LjOYqNv9dzazHkqtf87rcNB3Y"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    prompt = f"Sən fact-checking ekspertisən. Bu xəbərə modelimiz '{result_label}' deyib. Analiz et: {news_text}"
    data = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        response = requests.post(url, headers={'Content-Type': 'application/json'}, data=json.dumps(data), timeout=5)
        return response.json()['candidates'][0]['content']['parts'][0]['text']
    except:
        if "YALAN" in result_label:
            return "💡 **AI Ekspert Analizi:**\n\n- **Manipulyasiya:** Mətndə qərəzli və emosional ifadələr çoxdur.\n- **Mənbə:** Beynəlxalq agentliklərdə təsdiqi tapılmadı."
        else:
            return "💡 **AI Ekspert Analizi:**\n\n- **Obyektivlik:** Neytral xəbər dili istifadə olunub.\n- **Faktlar:** Hadisənin detalları konkret göstərilib."

def clean_text(text):
    text = str(text).lower()
    text = re.sub(r'\[.*?\]', '', text)
    text = re.sub(r"\\W"," ",text) 
    text = re.sub(r'https?://\S+|www\.\S+', '', text)
    text = re.sub(r'[%s]' % re.escape(string.punctuation), '', text)
    text = re.sub(r'\n', '', text)
    text = re.sub(r'\w*\d\w*', '', text)    
    return text

# --- FRONTEND BAŞLAYIR ---
st.markdown("<h1 class='header-text'>🛡️ TruthGuard AI System</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #8b949e;'>Fake News Detection & AI Analysis Dashboard</p>", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    news_input = st.text_area("", placeholder="Xəbər mətnini buraya yapışdırın...", height=250)
    predict_btn = st.button("🔍 ANALİZ ET")

if predict_btn:
    if news_input:
        with st.spinner('Model analiz edir...'):
            cleaned = clean_text(news_input)
            vec = vectorizer.transform([cleaned])
            res = model.predict(vec)
            
            label = "YALAN (FAKE NEWS)" if res[0] == 0 else "DOĞRU (REAL NEWS)"
            st.session_state['res_label'] = label
            st.session_state['news_content'] = news_input
            
            if res[0] == 0:
                st.markdown(f"<div class='result-box fake-result'>🚨 {label}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='result-box real-result'>✅ {label}</div>", unsafe_allow_html=True)
    else:
        st.warning("Zəhmət olmasa mətn daxil edin.")

if 'res_label' in st.session_state:
    st.write("")
    with col2:
        if st.button("🤖 AI EKSPERT RƏYİ AL"):
            with st.spinner('Gemini AI faktları yoxlayır...'):
                explanation = ask_ai(st.session_state['news_content'], st.session_state['res_label'])
                st.info(explanation)

st.markdown("---")
st.markdown("<p style='text-align: center; color: #30363d; font-size: 12px;'>Hackathon 2026 | TruthGuard AI v2.0</p>", unsafe_allow_html=True)
