import streamlit as st
import google.generativeai as genai
from PIL import Image
import pytesseract
from GoogleNews import GoogleNews
import speech_recognition as sr
from deep_translator import GoogleTranslator
import firebase_admin
from firebase_admin import credentials, auth
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.tools import run_flow
from oauth2client.file import Storage
from authlib.integrations.requests_client import OAuth2Session  # مكتبة authlib لتسجيل الدخول عبر Facebook

# إعداد عنوان الصفحة والأيقونة
st.set_page_config(
    page_title="مساعد الذكاء الصناعي للقدس",
    page_icon="icon.png",  # استبدل باسم ملف الأيقونة
    layout="wide",
)

# تهيئة Firebase (مرة واحدة فقط)
if not firebase_admin._apps:
    cred = credentials.Certificate("jerusalemguide-f62df524-firebase-adminsdk-rx86y-a5105a0042.json")  # استخدم المسار الصحيح
    firebase_admin.initialize_app(cred)

# تهيئة النموذج الذكاء الصناعي (Google Gemini AI)
genai.configure(api_key="AIzaSyBSJuDonuegkf9ONc86rzffFAywf9897n0")  # استبدل بمفتاح API الصحيح
model = genai.GenerativeModel('gemini-1.5-pro')

# تحديد مسار Tesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

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
            color: white;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

# إضافة خيار للتبديل بين اللغات
language = st.sidebar.selectbox("اختر اللغة", ["العربية", "الإنجليزية"])

# ترجمة النصوص بناءً على اللغة المختارة
if language == "الإنجليزية":
    st.write("Welcome to Jerusalem AI Assistant!")
    button_text = "Send"
    tab1_title = "Chat"
    tab2_title = "Image Analysis"
    tab3_title = "News"
    tab4_title = "Voice Search"
else:
    st.write("مرحبًا بكم في مساعد الذكاء الصناعي للقدس!")
    button_text = "إرسال"
    tab1_title = "المحادثة"
    tab2_title = "تحليل الصور"
    tab3_title = "الأخبار"
    tab4_title = "البحث الصوتي"

# تبويبات للوظائف المختلفة
tab1, tab2, tab3, tab4 = st.tabs([tab1_title, tab2_title, tab3_title, tab4_title])

# تبويب المحادثة
with tab1:
    st.header(tab1_title)
    
    # تهيئة session_state لحفظ المحادثات
    if 'conversations' not in st.session_state:
        st.session_state.conversations = []
    
    user_input = st.text_input("اكتب سؤالك هنا:" if language == "العربية" else "Type your question here:")
    
    # إضافة زر للتبديل بين المحرك العام ومحرك القدس
    engine_mode = st.radio("اختر المحرك:" if language == "العربية" else "Choose Engine:", ["عام", "القدس"] if language == "العربية" else ["General", "Jerusalem"])
    
    if st.button(button_text):
        if user_input:
            if engine_mode == "القدس" or engine_mode == "Jerusalem":
                if "القدس" not in user_input and "Jerusalem" not in user_input:
                    st.warning("يرجى إدخال سؤال خاص بمدينة القدس فقط." if language == "العربية" else "Please enter a question about Jerusalem only.")
                else:
                    response = model.generate_content(f"أجب عن السؤال التالي بخصوص القدس فقط: {user_input}" if language == "العربية" else f"Answer the following question about Jerusalem only: {user_input}")
            else:
                response = model.generate_content(user_input)
            
            # حفظ المحادثة في session_state
            st.session_state.conversations.append({"user": user_input, "ai": response.text})
            st.write("الإجابة:" if language == "العربية" else "Answer:")
            st.write(response.text)
        else:
            st.write("الرجاء إدخال سؤال." if language == "العربية" else "Please enter a question.")

    # عرض جميع المحادثات السابقة
    if st.session_state.conversations:
        st.write("المحادثات السابقة:" if language == "العربية" else "Previous Conversations:")
        for i, conv in enumerate(st.session_state.conversations):
            st.write(f"المستخدم: {conv['user']}" if language == "العربية" else f"User: {conv['user']}")
            st.write(f"المساعد: {conv['ai']}" if language == "العربية" else f"AI: {conv['ai']}")
            st.write("---")

# تبويب تحليل الصور
with tab2:
    st.header(tab2_title)
    uploaded_image = st.file_uploader("قم بتحميل صورة تحتوي على نص" if language == "العربية" else "Upload an image containing text", type=["png", "jpg", "jpeg"])
    
    if uploaded_image is not None:
        image = Image.open(uploaded_image)
        st.image(image, caption="الصورة المرفوعة" if language == "العربية" else "Uploaded Image", use_container_width=True)
        
        # تحليل النص من الصورة
        text = pytesseract.image_to_string(image, lang='ara')
        st.write("النص المستخرج:" if language == "العربية" else "Extracted Text:")
        st.write(text)

# تبويب الأخبار
with tab3:
    st.header(tab3_title)
    googlenews = GoogleNews(lang='ar', region='PS')
    googlenews.search("القدس")
    
    for news in googlenews.result():
        st.subheader(news['title'])
        st.write(news['desc'])
        st.write("---")

# تبويب البحث الصوتي
with tab4:
    st.header(tab4_title)
    if st.button("بدء التسجيل الصوتي" if language == "العربية" else "Start Voice Recording"):
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            st.write("تكلم الآن..." if language == "العربية" else "Speak now...")
            audio = recognizer.listen(source)
        
        try:
            text = recognizer.recognize_google(audio, language="ar-AR" if language == "العربية" else "en-US")
            st.write("النص المسموع:" if language == "العربية" else "Recognized Text:")
            st.write(text)
            
            # ترجمة النص إلى الإنجليزية باستخدام deep-translator
            if language == "العربية":
                translator = GoogleTranslator(source='auto', target='en')
                translated = translator.translate(text)
                st.write("الترجمة إلى الإنجليزية:")
                st.write(translated)
        except sr.UnknownValueError:
            st.write("لم يتم التعرف على الصوت" if language == "العربية" else "Could not understand audio")
        except sr.RequestError:
            st.write("حدث خطأ أثناء تحويل الصوت إلى نص" if language == "العربية" else "Error converting speech to text")

# إضافة تسجيل الدخول عبر Google وFacebook
st.sidebar.title("تسجيل الدخول")

# تسجيل الدخول عبر Google
redirect_uri = "https://your-app-url.com"  # استبدل بالرابط العام لتطبيقك
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
    redirect_uri=redirect_uri,  # استخدم نفس الرابط العام
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