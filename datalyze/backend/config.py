# Application Configuration
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(os.path.dirname(BASE_DIR), 'frontend')

# Flask settings
SECRET_KEY = 'datalyze_secret_key_2024_secure'
MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB max upload size

# Runtime directories
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
REPORTS_FOLDER = os.path.join(BASE_DIR, 'reports')

# Database configuration
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'datalyze.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False

# SMTP Email Settings (Configure these to send real emails to users' inboxes)
# For Gmail: Use 'smtp.gmail.com', port 587, and a 16-character Google App Password
SMTP_SERVER = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.environ.get('SMTP_PORT', 587))
SMTP_EMAIL = os.environ.get('SMTP_EMAIL', '')        # e.g. 'youremail@gmail.com'
SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD', '')  # 16-character Google App Password

# Color palette for charts
PALETTE = [
    '#6C63FF', '#FF6584', '#43E97B', '#F7971E', '#4FACFE',
    '#FF9A9E', '#A18CD1', '#FCCB90', '#D4FC79', '#96FBC4'
]
