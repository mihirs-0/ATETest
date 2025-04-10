import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
from typing import Dict, List, Optional
import json
from datetime import datetime

class AlertSystem:
    def __init__(self, 
                 email_config: Optional[Dict] = None,
                 slack_config: Optional[Dict] = None):
        """
        Initialize the alert system.
        
        Args:
            email_config: Dictionary with email configuration
            slack_config: Dictionary with Slack configuration
        """
        self.email_config = email_config or {}
        self.slack_config = slack_config or {}
        
    def send_email_alert(self, 
                        subject: str,
                        message: str,
                        recipients: List[str]) -> bool:
        """
        Send email alert.
        
        Args:
            subject: Email subject
            message: Email message
            recipients: List of email recipients
            
        Returns:
            bool indicating success
        """
        if not self.email_config:
            return False
            
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_config.get('sender')
            msg['To'] = ', '.join(recipients)
            msg['Subject'] = subject
            
            msg.attach(MIMEText(message, 'plain'))
            
            with smtplib.SMTP(
                self.email_config.get('smtp_server'),
                self.email_config.get('smtp_port')
            ) as server:
                server.starttls()
                server.login(
                    self.email_config.get('username'),
                    self.email_config.get('password')
                )
                server.send_message(msg)
                
            return True
        except Exception as e:
            print(f"Failed to send email alert: {str(e)}")
            return False
            
    def send_slack_alert(self, 
                        message: str,
                        channel: Optional[str] = None) -> bool:
        """
        Send Slack alert.
        
        Args:
            message: Alert message
            channel: Optional Slack channel
            
        Returns:
            bool indicating success
        """
        if not self.slack_config:
            return False
            
        try:
            webhook_url = self.slack_config.get('webhook_url')
            if not webhook_url:
                return False
                
            payload = {
                'text': message,
                'channel': channel or self.slack_config.get('default_channel', '#alerts')
            }
            
            response = requests.post(
                webhook_url,
                data=json.dumps(payload),
                headers={'Content-Type': 'application/json'}
            )
            
            return response.status_code == 200
        except Exception as e:
            print(f"Failed to send Slack alert: {str(e)}")
            return False
            
    def format_yield_alert(self, 
                          alert_data: Dict,
                          alert_type: str = 'Yield Drop') -> str:
        """
        Format yield alert message.
        
        Args:
            alert_data: Dictionary with alert data
            alert_type: Type of alert
            
        Returns:
            Formatted alert message
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return f"""
        [{timestamp}] {alert_type} Alert
        -------------------------
        Wafer ID: {alert_data['wafer_id']}
        Current Yield: {alert_data['rolling_yield']:.2%}
        Severity: {alert_data['severity']}
        """
        
    def send_alert(self, 
                  alert_data: Dict,
                  alert_type: str = 'Yield Drop',
                  recipients: Optional[List[str]] = None,
                  slack_channel: Optional[str] = None) -> bool:
        """
        Send alert through configured channels.
        
        Args:
            alert_data: Dictionary with alert data
            alert_type: Type of alert
            recipients: Optional list of email recipients
            slack_channel: Optional Slack channel
            
        Returns:
            bool indicating success
        """
        message = self.format_yield_alert(alert_data, alert_type)
        
        email_success = True
        if self.email_config and recipients:
            email_success = self.send_email_alert(
                subject=f"{alert_type} Alert",
                message=message,
                recipients=recipients
            )
            
        slack_success = True
        if self.slack_config:
            slack_success = self.send_slack_alert(
                message=message,
                channel=slack_channel
            )
            
        return email_success and slack_success 