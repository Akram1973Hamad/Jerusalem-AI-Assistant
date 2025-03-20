# config.py

import os

# 🔑 مفاتيح API
GEMINI_API_KEY = "AIzaSyBSJuDonuegkf9ONc86rzffFAywf9897n0"
NEWS_API_KEY = "b29cce25f323455a983ccb77ff159305"

# 📁 المسارات
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
IMAGE_PATH = os.path.join(ASSETS_DIR, "aqsa_background.jpg")
ICON_PATH = os.path.join(ASSETS_DIR, "app_icon.ico")
DB_PATH = os.path.join(BASE_DIR, "chat_history.db")

# 🎨 الألوان
LIGHT_MODE = {"bg": "#f8f9fa", "fg": "#000"}
DARK_MODE = {"bg": "#212529", "fg": "#fff"}
