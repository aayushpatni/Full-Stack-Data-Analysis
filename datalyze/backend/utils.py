# Utility / Helper Functions
import os
import random
import string
import hashlib
import io
import base64
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import matplotlib.pyplot as plt

from config import SMTP_SERVER, SMTP_PORT, SMTP_EMAIL, SMTP_PASSWORD


def generate_otp():
    """Generate a random 6-digit OTP string."""
    return ''.join(random.choices(string.digits, k=6))


def send_otp_email(to_email, otp, purpose="Login"):
    """
    Sends an OTP email to the user if SMTP is configured.
    Returns (success: bool, message: str).
    """
    if not SMTP_EMAIL or not SMTP_PASSWORD:
        return False, "SMTP credentials not configured"

    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f'Datalyze {purpose} Code: {otp}'
        msg['From'] = f"Datalyze <{SMTP_EMAIL}>"
        msg['To'] = to_email

        html = f"""<!DOCTYPE html>
<html>
<body style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #080812; color: #E8E8F0; padding: 30px; margin: 0;">
  <div style="max-width: 480px; margin: 0 auto; background: #1A1A2E; border: 1px solid #252540; border-radius: 16px; padding: 32px; text-align: center;">
    <h1 style="color: #6C63FF; margin-top: 0;">🧬 Datalyze</h1>
    <h3 style="color: #FFFFFF; font-weight: 600;">{purpose} Verification Code</h3>
    <p style="color: #7A7A9A; font-size: 14px;">Use the 6-digit OTP below to verify your account.</p>
    <div style="margin: 28px 0; background: #161628; border: 1px dashed #6C63FF; border-radius: 12px; padding: 16px;">
      <span style="font-size: 32px; font-weight: bold; letter-spacing: 8px; color: #6C63FF;">{otp}</span>
    </div>
    <p style="color: #7A7A9A; font-size: 12px;">This code will expire in 5 minutes. If you did not request this code, please ignore this email.</p>
  </div>
</body>
</html>"""
        msg.attach(MIMEText(html, 'html'))

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=10)
        server.starttls()
        server.login(SMTP_EMAIL, SMTP_PASSWORD)
        server.sendmail(SMTP_EMAIL, [to_email], msg.as_string())
        server.quit()
        return True, "Email sent successfully"
    except Exception as e:
        print(f"[SMTP Error] Failed sending OTP email to {to_email}: {e}")
        return False, str(e)


def b64_fig(fig):
    """Render a Matplotlib figure to a base64-encoded PNG string and close it."""
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=130, bbox_inches='tight',
                facecolor='#0F0F1A', edgecolor='none')
    buf.seek(0)
    img = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)
    return img


def styled_fig(w=10, h=5):
    """Create a dark-themed Matplotlib figure + axes pair."""
    fig, ax = plt.subplots(figsize=(w, h))
    fig.patch.set_facecolor('#0F0F1A')
    ax.set_facecolor('#161628')
    ax.tick_params(colors='#AAA', labelsize=9)
    ax.xaxis.label.set_color('#CCC')
    ax.yaxis.label.set_color('#CCC')
    ax.title.set_color('#EEE')
    for spine in ax.spines.values():
        spine.set_edgecolor('#333')
    ax.grid(True, color='#222', linewidth=0.5, alpha=0.7)
    return fig, ax
