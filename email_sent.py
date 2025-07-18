import pandas as pd
import qrcode
import os
import smtplib
from email.message import EmailMessage
from email.utils import formataddr
from email.mime.base import MIMEBase
from email import encoders
from dotenv import load_dotenv 

load_dotenv()

FROM_EMAIL = "bbbd68859@gmail.com"
PASSWORD =os.getenv("EMAIL_PASSWORD")
HOST = os.getenv("SMTP")
PORT = os.getenv("CONNECT")

def send_email(full_name, doctor, department, appointment_time, age, gender, to_email):
    
    qr_content = (
        f"Appointment Confirmation\n"
        f"Name: {full_name}\n"
        f"Age: {age}\n"
        f"Gender: {gender}\n"
        f"Doctor: {doctor}\n"
        f"Department: {department}\n"
        f"Time: {appointment_time}"
    )
    qr_filename = f"{full_name.replace(' ', '_')}_appointment_qr.png"
    qr = qrcode.make(qr_content)
    qr.save(qr_filename)

    
    msg = EmailMessage()
    msg['Subject'] = f"✅ Appointment Confirmed with {doctor}"
    msg['From'] = formataddr(("MedAssist Lumina", FROM_EMAIL))
    msg['To'] = to_email
    
    msg.add_alternative(f"""
       <html>
  <body style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f0f4f8; padding: 30px;">
    <div style="max-width: 650px; margin: auto; background: #ffffff; border-radius: 12px; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1); overflow: hidden;">
      <div style="background: linear-gradient(to right, #43cea2, #185a9d); padding: 20px;">
        <h2 style="color: #ffffff; text-align: center; margin: 0;">✅ Appointment Confirmed</h2>
      </div>

      <div style="padding: 30px;">
        <p style="font-size: 16px;">Dear <strong>{full_name}</strong>,</p>
        <p style="font-size: 15px;">We're pleased to confirm your doctor appointment. Please find the details below:</p>

        <table style="width: 100%; border-collapse: collapse; margin-top: 20px;">
          <tr>
            <td style="padding: 12px; border-bottom: 1px solid #e0e0e0;"><strong>👤 Patient Name:</strong></td>
            <td style="padding: 12px; border-bottom: 1px solid #e0e0e0;">{full_name}</td>
          </tr>
          <tr>
            <td style="padding: 12px; border-bottom: 1px solid #e0e0e0;"><strong>🍰 Age:</strong></td>
            <td style="padding: 12px; border-bottom: 1px solid #e0e0e0;">{age}</td>
          </tr>
          <tr>
            <td style="padding: 12px; border-bottom: 1px solid #e0e0e0;"><strong>🧑‍🦰 Gender:</strong></td>
            <td style="padding: 12px; border-bottom: 1px solid #e0e0e0;">{gender}</td>
          </tr>
          <tr>
            <td style="padding: 12px; border-bottom: 1px solid #e0e0e0;"><strong>👨‍⚕️ Doctor Name:</strong></td>
            <td style="padding: 12px; border-bottom: 1px solid #e0e0e0;">{doctor}</td>
          </tr>
          <tr>
            <td style="padding: 12px; border-bottom: 1px solid #e0e0e0;"><strong>🏬 Department:</strong></td>
            <td style="padding: 12px; border-bottom: 1px solid #e0e0e0;">{department}</td>
          </tr>
          <tr>
            <td style="padding: 12px;"><strong>🕒 Appointment Time:</strong></td>
            <td style="padding: 12px;">{appointment_time}</td>
          </tr>
        </table>

        <p style="margin-top: 25px; font-size: 15px;">📎 Please find your appointment QR code attached. It will be scanned at the reception desk.</p>

        <p style="margin-top: 20px; font-size: 15px;">Thank you for choosing <strong>MedAssist</strong>. We look forward to seeing you!</p>

        <p style="margin-top: 30px; font-weight: bold; font-size: 16px;">Warm regards,<br><span style="color: #185a9d;">The MedAssist Team</span></p>
      </div>

      <div style="background-color: #f7f7f7; text-align: center; padding: 10px; font-size: 12px; color: #777;">
        © 2025 MedAssist Inc. All rights reserved.
      </div>
    </div>
  </body>
</html>
""",subtype = 'html')
    
    with open(qr_filename, 'rb') as f:
        qr_data = f.read()
        msg.add_attachment(qr_data, maintype='image', subtype='png', filename=qr_filename)

    try:
        smtp = smtplib.SMTP(HOST, PORT)
        smtp.ehlo()
        smtp.starttls()
        smtp.login(FROM_EMAIL, PASSWORD)
        smtp.send_message(msg)
        #print(f"✅ Email sent to {to_email}")
    except Exception as e:
        print(f"❌ Failed to send email to {to_email}: {e}")
    finally:
        smtp.quit()
        if os.path.exists(qr_filename):
            os.remove(qr_filename)
