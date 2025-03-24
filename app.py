import streamlit as st
import google.generativeai as genai
from PIL import Image
from GoogleNews import GoogleNews
import speech_recognition as sr
from deep_translator import GoogleTranslator
import firebase_admin
from firebase_admin import credentials, auth
from google_auth_oauthlib.flow import InstalledAppFlow
from oauth2client.tools import run_flow
from oauth2client.file import Storage
from authlib.integrations.requests_client import OAuth2Session
import easyocr
from gtts import gTTS
import os
import json
from datetime import datetime
import folium
from streamlit_folium import folium_static
import numpy as np
import warnings


# إعداد عنوان الصفحة والأيقونة
st.set_page_config(
    page_title="مساعد الذكاء الصناعي للقدس",
    page_icon="assets/app_icon.ico",  # استبدل باسم ملف الأيقونة
    layout="wide",
)



import os

base_dir = os.path.dirname(os.path.abspath(__file__))  # احصل على مسار المجلد الحالي
cred_path = os.path.join(base_dir, "jerusalemguide-f62df524-firebase-adminsdk-rx86y-8df46b8ec5.json")

cred = credentials.Certificate(cred_path)

# تهيئة النموذج الذكاء الصناعي (Google Gemini AI)
genai.configure(api_key="AIzaSyBSJuDonuegkf9ONc86rzffFAywf9897n0")  # استبدل بمفتاح API الصحيح
model = genai.GenerativeModel('gemini-1.5-pro')

# تهيئة easyocr
reader = easyocr.Reader(['ar', 'en'])

# عنوان التطبيق
st.title("مساعد الذكاء الصناعي للقدس")

# إضافة خيار للوضع الداكن والنهاري
theme = st.sidebar.selectbox("اختر الوضع", ["نهاري", "ليلي"])

if theme == "ليلي":
    st.markdown(
        """
        <style>
        .stApp {
            background-color: #1E1E1E;
            color: #FFFFFF;
        }
        .stButton>button {
            background-color: #4CAF50;
            color: white;
        }
        .stTextInput>div>div>input {
            background-color: #2E2E2E;
            color: #FFFFFF;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
else:
    st.markdown(
        """
        <style>
        .stApp {
            background-color: #FFFFFF;
            color: #000000;
        }
        .stButton>button {
            background-color: #008CBA;
            color: black;
        }
        .stTextInput>div>div>input {
            background-color: #FFFFFF;
            color: #000000;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

# إضافة خيار للتبديل بين اللغات
language = st.sidebar.selectbox("اختر اللغة", ["العربية", "الإنجليزية"])

# ترجمة النصوص بناءً على اللغة المختارة
def translate_text(text, target_language):
    if target_language == "الإنجليزية":
        return GoogleTranslator(source='auto', target='en').translate(text)
    else:
        return GoogleTranslator(source='auto', target='ar').translate(text)

# تبويبات للوظائف المختلفة
tab1, tab2, tab3, tab4, tab5 = st.tabs(["المحادثة", "تحليل الصور", "الأخبار", "البحث الصوتي", "دليل القدس"])

# تبويب المحادثة
with tab1:
    st.header("المحادثة")
    
    # تهيئة session_state لحفظ المحادثات
    if 'conversations' not in st.session_state:
        st.session_state.conversations = []
    
    user_input = st.text_input("اكتب سؤالك هنا:" if language == "العربية" else "Type your question here:")
    
    # إضافة زر للتبديل بين المحرك العام ومحرك القدس
    engine_mode = st.radio("اختر المحرك:" if language == "العربية" else "Choose Engine:", ["عام", "القدس"] if language == "العربية" else ["General", "Jerusalem"])
    
    if st.button("إرسال" if language == "العربية" else "Send"):
        if user_input:
            if engine_mode == "القدس" or engine_mode == "Jerusalem":
                if "القدس" not in user_input and "Jerusalem" not in user_input:
                    st.warning("يرجى إدخال سؤال خاص بمدينة القدس فقط." if language == "العربية" else "Please enter a question about Jerusalem only.")
                else:
                    response = model.generate_content(f"أجب عن السؤال التالي بخصوص القدس فقط: {user_input}" if language == "العربية" else f"Answer the following question about Jerusalem only: {user_input}")
            else:
                response = model.generate_content(user_input)
            
            # حفظ المحادثة في session_state
            st.session_state.conversations.append({"user": user_input, "ai": response.text, "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
            st.write("الإجابة:" if language == "العربية" else "Answer:")
            st.write(response.text)
        else:
            st.write("الرجاء إدخال سؤال." if language == "العربية" else "Please enter a question.")

    # عرض جميع المحادثات السابقة
    if st.session_state.conversations:
        st.sidebar.title("المحادثات السابقة" if language == "العربية" else "Previous Conversations")
        for i, conv in enumerate(st.session_state.conversations):
            st.sidebar.write(f"المستخدم: {conv['user']}" if language == "العربية" else f"User: {conv['user']}")
            st.sidebar.write(f"المساعد: {conv['ai']}" if language == "العربية" else f"AI: {conv['ai']}")
            st.sidebar.write(f"الوقت: {conv['timestamp']}")
            st.sidebar.write("---")

# تهيئة easyocr
reader = easyocr.Reader(['ar', 'en'])

with tab2:
    st.header("تحليل الصور")
    
    # تحميل الصورة
    uploaded_image = st.file_uploader("قم بتحميل صورة", type=["png", "jpg", "jpeg"])
    
    if uploaded_image is not None:
        # عرض الصورة المرفوعة
        image = Image.open(uploaded_image)
        st.image(image, caption="الصورة المرفوعة", use_container_width=True)
        
        # تحويل الصورة إلى numpy array
        image_np = np.array(image)
        
        # استخراج النص من الصورة باستخدام easyocr
        result = reader.readtext(image_np)
        if result:
            st.write("النص المستخرج:")
            for detection in result:
                st.write(detection[1])  # النص المستخرج
        else:
            st.write("لم يتم العثور على نص في الصورة.")


# تبويب الأخبار
with tab3:
    st.header("الأخبار")
    googlenews = GoogleNews(lang='ar' if language == "العربية" else 'en', region='PS')
    googlenews.search("القدس" if language == "العربية" else "Jerusalem")
    
    for news in googlenews.result():
        st.subheader(news['title'])
        st.write(news['desc'])
        st.write("---")

# تبويب البحث الصوتي
with tab4:
    st.header("البحث الصوتي")
    if st.button("بدء التسجيل الصوتي" if language == "العربية" else "Start Voice Recording"):
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            st.write("تكلم الآن..." if language == "العربية" else "Speak now...")
            audio = recognizer.listen(source)
        
        try:
            text = recognizer.recognize_google(audio, language="ar-AR" if language == "العربية" else "en-US")
            st.write("النص المسموع:" if language == "العربية" else "Recognized Text:")
            st.write(text)
            
            # إرسال النص المسموع إلى النموذج الذكي
            response = model.generate_content(text)
            st.write("الإجابة:" if language == "العربية" else "Answer:")
            st.write(response.text)
            
            # تحويل الإجابة إلى صوت
            tts = gTTS(text=response.text, lang='ar' if language == "العربية" else 'en')
            tts.save("response.mp3")
            st.audio("response.mp3", format="audio/mp3")
        except sr.UnknownValueError:
            st.write("لم يتم التعرف على الصوت" if language == "العربية" else "Could not understand audio")
        except sr.RequestError:
            st.write("حدث خطأ أثناء تحويل الصوت إلى نص" if language == "العربية" else "Error converting speech to text")

# تبويب دليل القدس
with tab5:
    st.header("دليل القدس الشامل" if language == "العربية" else "Comprehensive Jerusalem Guide")
    
    # أقسام الدليل
    guide_section = st.selectbox(
        "اختر قسمًا:" if language == "العربية" else "Choose a section:",
        ["المعالم التاريخية والدينية", "المطاعم", "الفنادق", "الأنشطة الثقافية"] if language == "العربية" else ["Historical and Religious Landmarks", "Restaurants", "Hotels", "Cultural Activities"]
    )
    
    if guide_section == "المعالم التاريخية والدينية" or guide_section == "Historical and Religious Landmarks":
        st.subheader("المعالم التاريخية والدينية" if language == "العربية" else "Historical and Religious Landmarks")
        
        # المسجد الأقصى
        st.write("""
        - **المسجد الأقصى**: المسجد الثالث في الإسلام وأحد أهم المعالم الإسلامية.
        """)
        if st.button("عرض موقع المسجد الأقصى" if language == "العربية" else "Show Al-Aqsa Mosque Location"):
            # إحداثيات المسجد الأقصى
            map_location = folium.Map(location=[31.7761, 35.2358], zoom_start=15)
            folium.Marker([31.7761, 35.2358], popup="المسجد الأقصى" if language == "العربية" else "Al-Aqsa Mosque").add_to(map_location)
            folium_static(map_location)
        
        # قبة الصخرة
        st.write("""
        - **قبة الصخرة**: مبنى إسلامي ذو قبة ذهبية يقع داخل الحرم القدسي.
        """)
        if st.button("عرض موقع قبة الصخرة" if language == "العربية" else "Show Dome of the Rock Location"):
            # إحداثيات قبة الصخرة
            map_location = folium.Map(location=[31.7780, 35.2354], zoom_start=15)
            folium.Marker([31.7780, 35.2354], popup="قبة الصخرة" if language == "العربية" else "Dome of the Rock").add_to(map_location)
            folium_static(map_location)
        
        # كنيسة القيامة
        st.write("""
        - **كنيسة القيامة**: واحدة من أقدس الكنائس في العالم المسيحي.
        """)
        if st.button("عرض موقع كنيسة القيامة" if language == "العربية" else "Show Church of the Holy Sepulchre Location"):
            # إحداثيات كنيسة القيامة
            map_location = folium.Map(location=[31.7785, 35.2296], zoom_start=15)
            folium.Marker([31.7785, 35.2296], popup="كنيسة القيامة" if language == "العربية" else "Church of the Holy Sepulchre").add_to(map_location)
            folium_static(map_location)
        
        # حائط البراق
        st.write("""
        - **حائط البراق**: يعتبر من أشهر معالم مدينة القدس، ولهذا الحائط مكانة كبيرة عند أتباع الديانتين الإسلامية  إذ يُذكر في بعض المصادر الإسلامية على أنه الحائط الذي قام الرسول محمد ﷺ بربط البراق إليه في ليلة الإسراء والمعراج..
        """)
        if st.button("عرض موقع حائط البراق" if language == "العربية" else "Show Western Wall Location"):
            # إحداثيات حائط البراق
            map_location = folium.Map(location=[31.7767, 35.2345], zoom_start=15)
            folium.Marker([31.7767, 35.2345], popup="حائط البراق" if language == "العربية" else "Western Wall").add_to(map_location)
            folium_static(map_location)
    
    elif guide_section == "المطاعم" or guide_section == "Restaurants":
        st.subheader("المطاعم" if language == "العربية" else "Restaurants")
        
        # مطعم الزيتونة
        st.write("""
        - **مطعم الزيتونة**: يقدم أطباقًا فلسطينية تقليدية.
        """)
        if st.button("عرض موقع مطعم الزيتونة" if language == "العربية" else "Show Al-Zaytouna Restaurant Location"):
            # إحداثيات مطعم الزيتونة
            map_location = folium.Map(location=[31.7830, 35.2280], zoom_start=15)
            folium.Marker([31.7830, 35.2280], popup="مطعم الزيتونة" if language == "العربية" else "Al-Zaytouna Restaurant").add_to(map_location)
            folium_static(map_location)
        
        # مطعم القدس القديمة
        st.write("""
        - **مطعم القدس القديمة**: يطل على الحرم القدسي ويقدم وجبات عربية.
        """)
        if st.button("عرض موقع مطعم القدس القديمة" if language == "العربية" else "Show Old Jerusalem Restaurant Location"):
            # إحداثيات مطعم القدس القديمة
            map_location = folium.Map(location=[31.7765, 35.2340], zoom_start=15)
            folium.Marker([31.7765, 35.2340], popup="مطعم القدس القديمة" if language == "العربية" else "Old Jerusalem Restaurant").add_to(map_location)
            folium_static(map_location)
        
        # مقهى الروضة
        st.write("""
        - **مقهى الروضة**: مكان مثالي لتناول القهوة والحلويات.
        """)
        if st.button("عرض موقع مقهى الروضة" if language == "العربية" else "Show Al-Rawda Cafe Location"):
            # إحداثيات مقهى الروضة
            map_location = folium.Map(location=[31.7820, 35.2300], zoom_start=15)
            folium.Marker([31.7820, 35.2300], popup="مقهى الروضة" if language == "العربية" else "Al-Rawda Cafe").add_to(map_location)
            folium_static(map_location)
    
    elif guide_section == "الفنادق" or guide_section == "Hotels":
        st.subheader("الفنادق" if language == "العربية" else "Hotels")
        
        # فندق أمباسادور
        st.write("""
        - **فندق أمباسادور**: فندق فاخر في وسط القدس.
        """)
        if st.button("عرض موقع فندق أمباسادور" if language == "العربية" else "Show Ambassador Hotel Location"):
            # إحداثيات فندق أمباسادور
            map_location = folium.Map(location=[31.7850, 35.2200], zoom_start=15)
            folium.Marker([31.7850, 35.2200], popup="فندق أمباسادور" if language == "العربية" else "Ambassador Hotel").add_to(map_location)
            folium_static(map_location)
        
        # فندق القدس الدولي
        st.write("""
        - **فندق القدس الدولي**: يقع بالقرب من الحرم القدسي.
        """)
        if st.button("عرض موقع فندق القدس الدولي" if language == "العربية" else "Show Jerusalem International Hotel Location"):
            # إحداثيات فندق القدس الدولي
            map_location = folium.Map(location=[31.7800, 35.2300], zoom_start=15)
            folium.Marker([31.7800, 35.2300], popup="فندق القدس الدولي" if language == "العربية" else "Jerusalem International Hotel").add_to(map_location)
            folium_static(map_location)
        
        # فندق الكولوني
        st.write("""
        - **فندق الكولوني**: فندق تاريخي يقدم إقامة فريدة.
        """)
        if st.button("عرض موقع فندق الكولوني" if language == "العربية" else "Show Colony Hotel Location"):
            # إحداثيات فندق الكولوني
            map_location = folium.Map(location=[31.7750, 35.2250], zoom_start=15)
            folium.Marker([31.7750, 35.2250], popup="فندق الكولوني" if language == "العربية" else "Colony Hotel").add_to(map_location)
            folium_static(map_location)
    
    elif guide_section == "الأنشطة الثقافية" or guide_section == "Cultural Activities":
        st.subheader("الأنشطة الثقافية" if language == "العربية" else "Cultural Activities")
        
        # مهرجان القدس للثقافة والفنون
        st.write("""
        - **مهرجان القدس للثقافة والفنون**: يقام سنويًا في الصيف.
        """)
        if st.button("عرض موقع مهرجان القدس للثقافة والفنون" if language == "العربية" else "Show Jerusalem Culture and Arts Festival Location"):
            # إحداثيات مهرجان القدس للثقافة والفنون
            map_location = folium.Map(location=[31.7800, 35.2200], zoom_start=15)
            folium.Marker([31.7800, 35.2200], popup="مهرجان القدس للثقافة والفنون" if language == "العربية" else "Jerusalem Culture and Arts Festival").add_to(map_location)
            folium_static(map_location)
        
        # معرض فلسطين للفنون
        st.write("""
        - **معرض فلسطين للفنون**: يعرض أعمالًا لفنانين محليين ودوليين.
        """)
        if st.button("عرض موقع معرض فلسطين للفنون" if language == "العربية" else "Show Palestine Art Gallery Location"):
            # إحداثيات معرض فلسطين للفنون
            map_location = folium.Map(location=[31.7850, 35.2300], zoom_start=15)
            folium.Marker([31.7850, 35.2300], popup="معرض فلسطين للفنون" if language == "العربية" else "Palestine Art Gallery").add_to(map_location)
            folium_static(map_location)
        
        # جولات ثقافية
        st.write("""
        - **جولات ثقافية**: جولات إرشادية في أحياء القدس القديمة.
        """)
        if st.button("عرض موقع جولات ثقافية" if language == "العربية" else "Show Cultural Tours Location"):
            # إحداثيات جولات ثقافية
            map_location = folium.Map(location=[31.7760, 35.2340], zoom_start=15)
            folium.Marker([31.7760, 35.2340], popup="جولات ثقافية" if language == "العربية" else "Cultural Tours").add_to(map_location)
            folium_static(map_location)


# إضافة تسجيل الدخول عبر Google وFacebook
st.sidebar.title("تسجيل الدخول")

# تسجيل الدخول عبر Google
redirect_uri = "https://jerusalem-ai-assistant-m5pxic4rqhoshiwjjcfdkn.streamlit.app/"  # استبدل بالرابط العام لتطبيقك
flow = OAuth2WebServerFlow(
    client_id='802468228123-csjve6jnv8r9bv5c6r7ebs7kooj1741f.apps.googleusercontent.com',  # استبدل بـ client_id الخاص بك
    client_secret='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',  # استبدل بـ client_secret الخاص بك
    scope='https://www.googleapis.com/auth/userinfo.profile',
    redirect_uri=redirect_uri,
)

# تخزين بيانات الاعتماد
storage = Storage('credentials.data')

# زر تسجيل الدخول عبر Google
if st.sidebar.button("تسجيل الدخول عبر Google"):
    credentials = run_flow(flow, storage)
    if credentials.access_token:
        st.write("تم تسجيل الدخول بنجاح!")

# تسجيل الدخول عبر Facebook
facebook_client = OAuth2Session(
    client_id="1831786527570419",  # استبدل بـ client_id الخاص بك
    client_secret="44169622fcde26e0910bcace16ad8f02",  # استبدل بـ client_secret الخاص بك
    scope="email",  # الصلاحيات المطلوبة
    redirect_uri="https://jerusalem-ai-assistant-m5pxic4rqhoshiwjjcfdkn.streamlit.app/",  # استخدم نفس الرابط العام
)

# إنشاء رابط تسجيل الدخول
auth_url, state = facebook_client.create_authorization_url(
    "https://www.facebook.com/v12.0/dialog/oauth"
)

# زر تسجيل الدخول عبر Facebook
if st.sidebar.button("تسجيل الدخول عبر Facebook"):
    st.write(f"[انقر هنا لتسجيل الدخول عبر Facebook]({auth_url})")

# معالجة الرد من Facebook
if 'code' in st.query_params:
    code = st.query_params['code'][0]
    token = facebook_client.fetch_token(
        "https://graph.facebook.com/v12.0/oauth/access_token",
        authorization_response=st.query_params['redirect_uri'][0],
        code=code,
    )
    st.write(f"تم تسجيل الدخول بنجاح! Token: {token}")