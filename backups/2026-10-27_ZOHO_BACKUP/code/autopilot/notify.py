"""Alerts: Telegram and/or e-mail (both free, both optional).

Telegram: set TELEGRAM_BOT_TOKEN + TELEGRAM_CHAT_ID.
E-mail (Gmail): set MAIL_USER (your gmail), MAIL_APP_PASSWORD (Google "App password", 16 letters)
and optionally MAIL_TO (defaults to MAIL_USER) and MAIL_CC (extra address to copy).
"""
import json
import os
import smtplib
import urllib.request
from email.message import EmailMessage


def _telegram(text):
    token, chat = os.getenv("TELEGRAM_BOT_TOKEN"), os.getenv("TELEGRAM_CHAT_ID")
    if not (token and chat):
        return
    try:
        data = json.dumps({"chat_id": chat, "text": text[:3900], "disable_web_page_preview": True}).encode()
        req = urllib.request.Request(f"https://api.telegram.org/bot{token}/sendMessage", data=data,
                                     headers={"Content-Type": "application/json"})
        urllib.request.urlopen(req, timeout=15)
    except Exception as e:
        print(f"[notify] telegram failed: {e}")


def _email(text):
    user, pwd = os.getenv("MAIL_USER"), os.getenv("MAIL_APP_PASSWORD")
    if not (user and pwd):
        return
    to = os.getenv("MAIL_TO") or user
    msg = EmailMessage()
    msg["Subject"] = text.splitlines()[0][:120]
    from .config import CHANNEL_NAME
    msg["From"] = f"{CHANNEL_NAME} Bot <{user}>"
    msg["To"] = to
    cc = os.getenv("MAIL_CC", "")
    if cc and cc.lower() != to.lower():
        msg["Cc"] = cc
    msg.set_content(text)
    try:
        with smtplib.SMTP_SSL(os.getenv("MAIL_SMTP", "smtp.gmail.com"), 465, timeout=30) as s:
            s.login(user, pwd.replace(" ", ""))
            s.send_message(msg)
    except Exception as e:
        print(f"[notify] email failed: {e}")


def send(text):
    _telegram(text)
    _email(text)
