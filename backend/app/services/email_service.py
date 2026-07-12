from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import aiosmtplib
from app.config import settings


class EmailService:
    @staticmethod
    async def send_email(to_email: str, subject: str, html_body: str) -> bool:
        if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
            return False

        msg = MIMEMultipart("alternative")
        msg["From"] = settings.SMTP_FROM_EMAIL
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(html_body, "html"))

        try:
            await aiosmtplib.send(
                msg,
                hostname=settings.SMTP_HOST,
                port=settings.SMTP_PORT,
                username=settings.SMTP_USER,
                password=settings.SMTP_PASSWORD,
                start_tls=True,
            )
            return True
        except Exception:
            return False

    @staticmethod
    async def send_otp_email(to_email: str, otp_code: str) -> bool:
        subject = "Your OTP Code - AI Research Assistant"
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <h2>Email Verification</h2>
            <p>Your One-Time Password (OTP) for AI Research Assistant:</p>
            <h1 style="letter-spacing: 5px; background: #f0f0f0; padding: 15px;
                       text-align: center; font-size: 36px; border-radius: 8px;">
                {otp_code}
            </h1>
            <p>This code expires in {settings.OTP_EXPIRE_MINUTES} minutes.</p>
            <p>If you didn't request this, please ignore this email.</p>
        </body>
        </html>
        """
        return await EmailService.send_email(to_email, subject, html_body)


email_service = EmailService()
