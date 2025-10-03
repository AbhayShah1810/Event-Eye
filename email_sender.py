import pandas as pd
from dotenv import load_dotenv
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import ssl

load_dotenv() # Load environment variables from .env file

# --- CONFIGURATION (Uses SMTP keys from .env) ---
SMTP_SERVER = os.getenv('SMTP_SERVER')
SMTP_PORT = int(os.getenv('SMTP_PORT'))
SMTP_USERNAME = os.getenv('SMTP_USERNAME')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
SENDER_EMAIL = os.getenv('SENDER_EMAIL')
SENDER_NAME = os.getenv('SENDER_NAME')

def send_certificate_email(recipient_name, recipient_email, pdf_filepath, event_name="EventEye Hackathon"):
    """Sends a single email with the certificate attached using Gmail SMTP."""

    if not all([SMTP_USERNAME, SMTP_PASSWORD, SENDER_EMAIL]):
        return "Configuration Error: SMTP credentials missing in .env"
        
    try:
        # Create message container
        msg = MIMEMultipart()
        msg['From'] = f"{SENDER_NAME} <{SENDER_EMAIL}>"
        msg['To'] = recipient_email
        msg['Subject'] = f"Your Certificate of Completion for {event_name}!"
        
        # Email body (can be simple text)
        body = f"Dear {recipient_name},\n\nThank you for attending our event. Your personalized certificate is attached.\n\nBest regards,\n{SENDER_NAME}"
        msg.attach(MIMEBase('text', 'plain')) # Simple text body

        # Attach PDF file
        with open(pdf_filepath, "rb") as attachment:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())
        
        encoders.encode_base64(part)
        part.add_header(
            "Content-Disposition",
            f"attachment; filename= {recipient_name.replace(' ', '_')}_Certificate.pdf",
        )
        msg.attach(part)

        # Connect to Gmail SMTP server (securely)
        context = ssl.create_default_context()
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls(context=context) # Secure the connection
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.sendmail(SENDER_EMAIL, recipient_email, msg.as_string())

        return 'Sent'
        
    except smtplib.SMTPAuthenticationError:
        return "SMTP Error: Login failed. Check App Password and 2FA."
    except smtplib.SMTPRecipientsRefused:
        return "SMTP Error: Recipient email refused (bounced)."
    except Exception as e:
        return f"SMTP Exception: {str(e)}"

def bulk_send_certificates(results_df):
    """Iterates through the generated certificates and sends them."""
    
    send_df = results_df[results_df['status'] == 'Generated'].copy()
    
    if send_df.empty:
        print("No valid certificates to send.")
        return results_df

    for index, row in send_df.iterrows():
        send_status = send_certificate_email(row['name'], row['email'], row['filepath'])
        results_df.loc[index, 'status'] = send_status
        
    return results_df