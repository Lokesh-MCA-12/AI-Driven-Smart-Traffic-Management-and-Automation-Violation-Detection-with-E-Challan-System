"""
Notification Service - Email and SMS
"""

import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import Optional

from app.config import settings

logger = logging.getLogger(__name__)


class NotificationService:
    """Handles email and SMS notifications for challans."""

    @staticmethod
    async def send_email(
        to_email: str,
        subject: str,
        body_html: str,
        attachment_path: Optional[str] = None,
    ) -> bool:
        """Send an email notification."""
        try:
            msg = MIMEMultipart()
            msg["From"] = settings.SMTP_FROM
            msg["To"] = to_email
            msg["Subject"] = subject

            msg.attach(MIMEText(body_html, "html"))

            # Attach PDF if provided
            if attachment_path:
                try:
                    with open(attachment_path, "rb") as f:
                        part = MIMEBase("application", "pdf")
                        part.set_payload(f.read())
                        encoders.encode_base64(part)
                        part.add_header(
                            "Content-Disposition",
                            f"attachment; filename=challan.pdf",
                        )
                        msg.attach(part)
                except FileNotFoundError:
                    logger.warning(f"Attachment not found: {attachment_path}")

            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                server.starttls()
                if settings.SMTP_USER and settings.SMTP_PASSWORD:
                    server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.send_message(msg)

            logger.info(f"Email sent successfully to {to_email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False

    @staticmethod
    async def send_sms(phone: str, message: str) -> bool:
        """Send an SMS notification using Twilio."""
        try:
            if not all([settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN]):
                logger.warning("Twilio credentials not configured. SMS not sent.")
                return False

            from twilio.rest import Client

            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

            sms = client.messages.create(
                body=message,
                from_=settings.TWILIO_PHONE_NUMBER,
                to=phone,
            )

            logger.info(f"SMS sent to {phone}, SID: {sms.sid}")
            return True

        except Exception as e:
            logger.error(f"Failed to send SMS to {phone}: {str(e)}")
            return False

    @staticmethod
    def build_challan_email(
        owner_name: str,
        challan_number: str,
        violation_type: str,
        fine_amount: float,
        due_date: str,
        location: str,
        timestamp: str,
        payment_link: str = "#",
    ) -> str:
        """Build HTML email body for a challan notification."""
        violation_labels = {
            "red_light": "Red Light Violation",
            "no_helmet": "No Helmet",
            "no_seatbelt": "No Seatbelt",
            "overspeed": "Overspeeding",
            "wrong_lane": "Wrong Lane Driving",
        }

        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #f4f6f9; margin: 0; padding: 20px; }}
                .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.08); }}
                .header {{ background: linear-gradient(135deg, #1e3a5f 0%, #2d5f8a 100%); color: white; padding: 30px; text-align: center; }}
                .header h1 {{ margin: 0; font-size: 22px; letter-spacing: 1px; }}
                .header p {{ margin: 8px 0 0; opacity: 0.85; font-size: 14px; }}
                .body {{ padding: 30px; }}
                .info-row {{ display: flex; justify-content: space-between; padding: 12px 0; border-bottom: 1px solid #eee; }}
                .info-label {{ color: #666; font-size: 14px; }}
                .info-value {{ font-weight: 600; color: #1e3a5f; font-size: 14px; }}
                .fine-box {{ background: #fff3f3; border: 2px solid #e74c3c; border-radius: 8px; padding: 20px; text-align: center; margin: 20px 0; }}
                .fine-amount {{ font-size: 32px; font-weight: 700; color: #e74c3c; }}
                .pay-btn {{ display: block; text-align: center; background: linear-gradient(135deg, #27ae60, #2ecc71); color: white; padding: 14px 30px; border-radius: 8px; text-decoration: none; font-weight: 600; margin: 20px auto; max-width: 250px; }}
                .footer {{ background: #f8f9fa; padding: 20px; text-align: center; font-size: 12px; color: #999; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🚦 Traffic Violation Notice</h1>
                    <p>Smart Traffic Management Authority</p>
                </div>
                <div class="body">
                    <p>Dear <strong>{owner_name}</strong>,</p>
                    <p>A traffic violation has been detected and recorded against your vehicle. Details below:</p>

                    <div class="info-row">
                        <span class="info-label">Challan No.</span>
                        <span class="info-value">{challan_number}</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">Violation</span>
                        <span class="info-value">{violation_labels.get(violation_type, violation_type)}</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">Location</span>
                        <span class="info-value">{location}</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">Date & Time</span>
                        <span class="info-value">{timestamp}</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">Due Date</span>
                        <span class="info-value">{due_date}</span>
                    </div>

                    <div class="fine-box">
                        <p style="margin:0 0 5px; color:#666;">Fine Amount</p>
                        <div class="fine-amount">₹{fine_amount:.2f}</div>
                    </div>

                    <a href="{payment_link}" class="pay-btn">Pay Fine Online →</a>

                    <p style="font-size: 13px; color: #999; margin-top: 20px;">
                        Please pay the fine before the due date to avoid additional penalties.
                        If you believe this is an error, contact the traffic authority within 15 days.
                    </p>
                </div>
                <div class="footer">
                    <p>This is an automated email from Smart Traffic Management System.</p>
                    <p>© 2026 Smart City Traffic Authority. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """

    @staticmethod
    def build_challan_sms(
        owner_name: str,
        challan_number: str,
        violation_type: str,
        fine_amount: float,
        due_date: str,
    ) -> str:
        """Build SMS message for challan notification."""
        violation_labels = {
            "red_light": "Red Light Violation",
            "no_helmet": "No Helmet",
            "no_seatbelt": "No Seatbelt",
            "overspeed": "Overspeeding",
            "wrong_lane": "Wrong Lane",
        }
        return (
            f"Dear {owner_name}, Traffic Violation Alert! "
            f"Challan #{challan_number} for {violation_labels.get(violation_type, violation_type)}. "
            f"Fine: Rs.{fine_amount:.0f}. Due: {due_date}. "
            f"Pay online to avoid late fees. -Smart Traffic Authority"
        )
