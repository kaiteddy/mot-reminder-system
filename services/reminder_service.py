"""
Reminder Service for MOT Reminder System

This service handles the scheduling and sending of reminders.
For local development, it simulates sending emails and SMS.
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
from datetime import datetime
import os

class ReminderService:
    def __init__(self):
        # Email settings
        self.smtp_server = os.environ.get('SMTP_SERVER', 'smtp.example.com')
        self.smtp_port = int(os.environ.get('SMTP_PORT', 587))
        self.smtp_username = os.environ.get('SMTP_USERNAME', 'user@example.com')
        self.smtp_password = os.environ.get('SMTP_PASSWORD', 'password')
        self.sender_email = os.environ.get('SENDER_EMAIL', 'garage@example.com')
        
        # SMS settings
        self.sms_api_url = os.environ.get('SMS_API_URL', 'https://api.sms-provider.com')
        self.sms_api_key = os.environ.get('SMS_API_KEY', 'your_api_key')
        self.sms_sender_id = os.environ.get('SMS_SENDER_ID', 'GarageReminder')
    
    def send_email_reminder(self, customer_email, subject, message):
        """
        Send an email reminder.
        For local development, this simulates sending an email.
        """
        # In a real implementation, this would send an actual email
        # try:
        #     msg = MIMEMultipart()
        #     msg['From'] = self.sender_email
        #     msg['To'] = customer_email
        #     msg['Subject'] = subject
        #     
        #     msg.attach(MIMEText(message, 'plain'))
        #     
        #     server = smtplib.SMTP(self.smtp_server, self.smtp_port)
        #     server.starttls()
        #     server.login(self.smtp_username, self.smtp_password)
        #     server.send_message(msg)
        #     server.quit()
        #     
        #     return True, "Email sent successfully"
        # except Exception as e:
        #     return False, str(e)
        
        # For local development, just log the email
        print(f"[SIMULATED EMAIL] To: {customer_email}, Subject: {subject}")
        print(f"Message: {message}")
        return True, "Email simulated successfully"
    
    def send_sms_reminder(self, phone_number, message):
        """
        Send an SMS reminder.
        For local development, this simulates sending an SMS.
        """
        # In a real implementation, this would send an actual SMS
        # try:
        #     payload = {
        #         'to': phone_number,
        #         'from': self.sms_sender_id,
        #         'message': message
        #     }
        #     
        #     headers = {
        #         'Authorization': f'Bearer {self.sms_api_key}',
        #         'Content-Type': 'application/json'
        #     }
        #     
        #     response = requests.post(self.sms_api_url, json=payload, headers=headers)
        #     response.raise_for_status()
        #     
        #     return True, "SMS sent successfully"
        # except Exception as e:
        #     return False, str(e)
        
        # For local development, just log the SMS
        print(f"[SIMULATED SMS] To: {phone_number}")
        print(f"Message: {message}")
        return True, "SMS simulated successfully"
    
    def format_reminder_message(self, template, vehicle, customer):
        """Format a reminder message with vehicle and customer details"""
        mot_expiry_date = vehicle.get('mot_expiry', 'Unknown')
        if isinstance(mot_expiry_date, datetime):
            mot_expiry_date = mot_expiry_date.strftime('%d/%m/%Y')
        
        return template.format(
            customer_name=customer.get('name', 'Customer'),
            vehicle_make=vehicle.get('make', 'Unknown'),
            vehicle_model=vehicle.get('model', 'Unknown'),
            vehicle_registration=vehicle.get('registration', 'Unknown'),
            mot_expiry_date=mot_expiry_date
        )
    
    def process_reminder(self, reminder, vehicle, customer, email_template, sms_template):
        """Process a reminder by sending email and/or SMS"""
        results = {
            'email': {'sent': False, 'message': 'Not attempted'},
            'sms': {'sent': False, 'message': 'Not attempted'}
        }
        
        # Send email if customer has email
        if customer.get('email'):
            email_message = self.format_reminder_message(email_template, vehicle, customer)
            subject = f"MOT Reminder for {vehicle.get('registration', 'your vehicle')}"
            success, message = self.send_email_reminder(customer['email'], subject, email_message)
            results['email'] = {'sent': success, 'message': message}
        
        # Send SMS if customer has phone
        if customer.get('phone'):
            sms_message = self.format_reminder_message(sms_template, vehicle, customer)
            success, message = self.send_sms_reminder(customer['phone'], sms_message)
            results['sms'] = {'sent': success, 'message': message}
        
        return results
