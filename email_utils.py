#email message template from Python Standard Library
from email.message import EmailMessage
#send the email
import aiosmtplib
#use template for HTML emails
from fastapi.templating import Jinja2Templates
from config import settings

#Jinja template loader pointintg at templates directory
#used to render HTML email bodies
templates = Jinja2Templates(directory="templates")


#send email function
async def send_email(
    to_email: str,
    subject: str,
    plain_text: str,
    html_content: str | None = None,
) -> None:
    #email header
    message = EmailMessage()
    message["From"] = settings.mail_from
    message["To"] = to_email
    message["subject"] = subject

    #email body
    message.set_content(plain_text)
    #treat html version as alternative version of the same content
    if html_content:
        message.add_alternative(html_content, subtype="html")

    #send the email
    await aiosmtplib.send(
        message,
        hostname=settings.mail_server,
        port=settings.mail_port,
        username=settings.mail_username if settings.mail_username else None,
        password=settings.mail_password.get_secret_value(),
        start_tls=settings.mail_use_tls
    )

async def send_password_reset_email(to_email: str, username: str, token: str) -> None:
    reset_url = f"{settings.frontend_url}/reset-password?token={token}"

    template = templates.env.get_template("email/password_reset.html")
    #render the conent by passing the rendered parameteters
    html_content = template.render(reset_url=reset_url, username=username)

    plain_text = f"""Hi {username},

You requested to reset your password. Click the link below to set a new password:

{reset_url}

This link will expire in 1 hour.

If you didn't request this, you can safely ignore this email.

Best regards,
The FastAPI Blog Team
"""

    await send_email(
        to_email=to_email,
        subject="Reset Your Password - FastAPI Blog",
        plain_text=plain_text,
        html_content=html_content,
    )

