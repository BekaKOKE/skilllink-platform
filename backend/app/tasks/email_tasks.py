import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from backend.app.tasks.celery_app import celery_app
from backend.app.core.config import settings

logger = logging.getLogger("skilllink.tasks")

SMTP_HOST = settings.SMTP_HOST
SMTP_PORT = settings.SMTP_PORT
SMTP_USER = settings.SMTP_USER
SMTP_PASS = settings.SMTP_PASS
FROM_EMAIL = settings.FROM_EMAIL


def _send_email(to: str, subject: str, html_body: str) -> None:
    if not SMTP_USER:
        # Dev режим — просто печатаем в консоль
        logger.info(f"[EMAIL STUB] To={to} | Subject={subject}\n{html_body}")
        return

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = FROM_EMAIL
    msg["To"] = to
    msg.attach(MIMEText(html_body, "html"))

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.sendmail(FROM_EMAIL, to, msg.as_string())

    logger.info(f"[EMAIL] Sent '{subject}' to {to}")


@celery_app.task(name="tasks.send_email_confirmation", bind=True, max_retries=3, default_retry_delay=10)
def send_email_confirmation(self, user_email: str, user_name: str, token: str):
    confirm_url = f"https://skilllink.kz/confirm-email?token={token}"
    subject = "Подтвердите ваш email — SkillLink"
    html_body = f"""
    <h2>Привет, {user_name}!</h2>
    <p>Нажмите кнопку ниже чтобы подтвердить email:</p>
    <a href="{confirm_url}" style="
        display:inline-block;padding:12px 24px;background:#4F46E5;
        color:#fff;border-radius:6px;text-decoration:none;font-weight:bold
    ">Подтвердить email</a>
    <p>Ссылка действительна 24 часа.</p>
    """
    try:
        _send_email(user_email, subject, html_body)
    except Exception as exc:
        raise self.retry(exc=exc)


@celery_app.task(name="tasks.send_password_reset", bind=True, max_retries=3, default_retry_delay=10)
def send_password_reset(self, user_email: str, user_name: str, token: str):
    reset_url = f"https://skilllink.kz/reset-password?token={token}"
    subject = "Сброс пароля — SkillLink"
    html_body = f"""
    <h2>Привет, {user_name}!</h2>
    <p>Запрос на сброс пароля для вашего аккаунта:</p>
    <a href="{reset_url}" style="
        display:inline-block;padding:12px 24px;background:#DC2626;
        color:#fff;border-radius:6px;text-decoration:none;font-weight:bold
    ">Сбросить пароль</a>
    <p>Ссылка действительна 30 минут.</p>
    """
    try:
        _send_email(user_email, subject, html_body)
    except Exception as exc:
        raise self.retry(exc=exc)