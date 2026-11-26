import os

from dotenv import load_dotenv

load_dotenv()
SECRET = os.environ["SECRET_KEY"]
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
MAIL_FROM = os.getenv("MAIL_FROM")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///database.db")
