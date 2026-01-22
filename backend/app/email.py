
import aiosmtplib
from email.message import EmailMessage
from app.config import settings
import logging

logger = logging.getLogger(__name__)

async def send_email(to_email: str, subject: str, body: str) -> None:
    """
    Sends an email using the configured SMTP server.
    In development/MVP, this might just log if credentials aren't set or if sending fails.
    """

    # Validation for testing environment where we might not have real credentials
    if settings.SMTP_HOST == "smtp.example.com":
        logger.info(f"EMAIL SIMULATION - To: {to_email}, Subject: {subject}, Body: {body}")
        print(f"EMAIL SIMULATION - To: {to_email}, Subject: {subject}, Body: {body}")
        return

    message = EmailMessage()
    message["From"] = settings.EMAIL_FROM
    message["To"] = to_email
    message["Subject"] = subject
    message.set_content(body)

    try:
        await aiosmtplib.send(
            message,
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            username=settings.SMTP_USER,
            password=settings.SMTP_PASSWORD,
            use_tls=True if settings.SMTP_PORT == 465 else False,
            start_tls=True if settings.SMTP_PORT == 587 else False,
        )
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {str(e)}")
        # For MVP, we print to stdout to ensure the user can see the OTP if email fails
        print(f"EMAIL FAILED (Fallback Log) - To: {to_email}, Subject: {subject}, Body: {body}")

async def send_otp_email(to_email: str, otp: str) -> None:
    subject = "Verify your MedStory account"
    body = f"Your verification code is: {otp}\n\nThis code expires in 10 minutes."
    await send_email(to_email, subject, body)
