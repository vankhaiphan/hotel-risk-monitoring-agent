import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import List, Dict, Optional
from src.config import SMTP_SERVER, SMTP_PORT, EMAIL_FROM, EMAIL_PASSWORD, EMAIL_TO

class Alerter:
    """Send risk alerts via email."""
    
    def __init__(self):
        self.smtp_server = SMTP_SERVER
        self.smtp_port = SMTP_PORT
        self.email_from = EMAIL_FROM
        self.email_password = EMAIL_PASSWORD
        self.email_to = EMAIL_TO
    
    def send_alerts(self, alerts: List[Dict]) -> bool:
        """
        Send email with all alerts.
        
        Args:
            alerts: List of alert dictionaries
        
        Returns:
            True if sent successfully, False otherwise
        """
        if not alerts:
            return True  # No alerts to send
        
        if not self.email_from or not self.email_password:
            print("⚠️  Email not configured. Alerts will be displayed below:")
            self._print_alerts(alerts)
            return False
        
        try:
            html_content = self._format_email_html(alerts)
            whatsapp_content = self._format_whatsapp_message(alerts)
            
            message = MIMEMultipart('alternative')
            message['Subject'] = f"🚨 Hotel Risk Alert - {len(alerts)} Event(s) Detected"
            message['From'] = self.email_from
            message['To'] = ', '.join(self.email_to)
            
            # Attach text version
            text_part = MIMEText(whatsapp_content, 'plain')
            message.attach(text_part)
            
            # Attach HTML version
            html_part = MIMEText(html_content, 'html')
            message.attach(html_part)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_from, self.email_password)
                server.send_message(message)
            
            print(f"✓ Email alert sent to {len(self.email_to)} recipient(s)")
            return True
        
        except Exception as e:
            print(f"✗ Error sending email: {e}")
            self._print_alerts(alerts)
            return False
    
    def _format_email_html(self, alerts: List[Dict]) -> str:
        """Format alerts as HTML email."""
        html = """<html>
<head>
<style>
body {{ font-family: Arial, sans-serif; color: #333; }}
.alert-container {{ margin: 20px; }}
.alert-box {{ 
border-left: 4px solid #dc3545;
padding: 15px;
margin: 15px 0;
background-color: #f8eef0;
border-radius: 4px;
}}
.hotel-name {{ font-size: 18px; font-weight: bold; color: #dc3545; }}
.event-type {{ font-size: 14px; background-color: #dc3545; color: white; padding: 4px 8px; border-radius: 3px; display: inline-block; margin: 5px 0; }}
.impact {{ margin: 10px 0; padding: 10px; background-color: #fff; border-radius: 3px; }}
.meta {{ font-size: 12px; color: #666; margin-top: 10px; }}
</style>
</head>
<body>
<div class="alert-container">
<h1>⚠️ Daily Hotel Risk Briefing</h1>
<p><strong>{0} high-risk event(s) detected on {1}</strong></p>
""".format(len(alerts), datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        
        for alert in alerts:
            html += f"""<div class="alert-box">
<p class="hotel-name">{alert['hotel_name']} - {alert['city']}, {alert['country']}</p>
<p class="event-type">{alert['event_type']}</p>
<p><strong>Event:</strong> {alert['title']}</p>
<div class="impact">
<strong>Impact Assessment:</strong><br/>
{alert['impact_assessment']}
</div>
<p><strong>Distance:</strong> {alert['distance']} km</p>
<p><strong>Source:</strong> {alert['source']}</p>
<p class="meta">
<strong>Date:</strong> {alert['published_at']}<br/>
<strong>Read More:</strong> <a href="{alert['url']}">{alert['url']}</a>
</p>
</div>
"""
        
        html += """<hr/>
<p style="font-size: 12px; color: #999;">
This is an automated alert from the Hotel Risk Monitoring Agent.
Please verify information and take appropriate action.
</p>
</div>
</body>
</html>
"""
        
        return html
    
    def _format_whatsapp_message(self, alerts: List[Dict]) -> str:
        """Format alerts as WhatsApp-style message."""
        message = f"""
⚠️ Daily Hotel Risk Briefing
{len(alerts)} alert(s) detected today.
{datetime.now().strftime('%Y-%m-%d')}

"""
        
        for i, alert in enumerate(alerts, 1):
            message += f"""
{i}. HOTEL: {alert['hotel_name']}
   LOCATION: {alert['city']}, {alert['country']}
   EVENT: {alert['title']}
   TYPE: {alert['event_type']}
   DISTANCE: {alert['distance']} km
   IMPACT: {alert['impact_assessment']}
   SOURCE: {alert['source']}
   DATE: {alert['published_at']}

"""
        
        message += "---\nEND OF MESSAGE"
        return message
    
    def _print_alerts(self, alerts: List[Dict]) -> None:
        """Print alerts to console."""
        print("\n" + "="*70)
        print("⚠️  HOTEL RISK ALERTS")
        print("="*70)
        
        for alert in alerts:
            print(f"\n⚠️ HOTEL RISK ALERT")
            print(f"Hotel: {alert['hotel_name']}")
            print(f"City: {alert['city']}")
            print(f"Country: {alert['country']}")
            print(f"\nEvent: {alert['title']}")
            print(f"Severity: HIGH")
            print(f"Distance: {alert['distance']} km")
            print(f"\nImpact Assessment:")
            print(f"{alert['impact_assessment']}")
            print(f"\nSource: {alert['source']}")
            print(f"Date: {alert['published_at']}")
            print(f"URL: {alert['url']}")
            print("-"*70)
        
        print("="*70 + "\n")
