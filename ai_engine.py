# ai_engine.py

import google.generativeai as genai
from config import GEMINI_API_KEY
from textblob import TextBlob

# 🔥 تهيئة الذكاء الصناعي
genai.configure(api_key=GEMINI_API_KEY)
model_general = genai.GenerativeModel("gemini-1.5-pro")
model_jerusalem = genai.GenerativeModel("gemini-1.5-pro")

# 🏆 اختيار المحرك
selected_model = model_general
selected_mode = "عام"

def toggle_model():
    global selected_model, selected_mode
    selected_model = model_jerusalem if selected_mode == "عام" else model_general
    selected_mode = "القدس" if selected_mode == "عام" else "عام"
    return selected_mode

# 🧠 التفاعل الذكي وتحليل المحادثات
def analyze_sentiment(text):
    analysis = TextBlob(text)
    if analysis.sentiment.polarity > 0:
        return "يبدو أنك سعيد! 😊 كيف يمكنني مساعدتك؟"
    elif analysis.sentiment.polarity < 0:
        return "أشعر أنك لست بحالة جيدة 😢، كيف يمكنني مساعدتك؟"
    else:
        return "أهلاً بك! كيف يمكنني مساعدتك اليوم؟"

# 📢 إنشاء نص ذكي باستخدام الذكاء الصناعي
def generate_smart_text(prompt):
    try:
        response = selected_model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"❌ خطأ أثناء إنشاء النص: {str(e)}"
