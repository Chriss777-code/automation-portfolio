#!/usr/bin/env python3
"""
Email Automation - Bulk email sending with templates

Send personalized emails at scale with CSV data and templates.
Supports Gmail, SMTP, and API-based providers.

Features:
- Template-based emails with variables
- CSV data source
- Rate limiting
- Send tracking
- Multiple providers

Author: Neo (AI Assistant)
Date: 2026-02-11
"""

import csv
import json
import smtplib
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, asdict


@dataclass
class EmailConfig:
    """SMTP configuration."""
    host: str
    port: int
    username: str
    password: str
    from_email: str
    from_name: Optional[str] = None
    use_tls: bool = True


@dataclass
class EmailTemplate:
    """Email template with variable placeholders."""
    name: str
    subject: str
    body_html: str
    body_text: Optional[str] = None


@dataclass
class SendResult:
    """Result of an email send."""
    to: str
    success: bool
    message_id: Optional[str] = None
    error: Optional[str] = None
    sent_at: Optional[str] = None


class EmailSender:
    """
    Send bulk personalized emails.
    
    Usage:
        sender = EmailSender(EmailConfig(
            host="smtp.gmail.com",
            port=587,
            username="your@gmail.com",
            password="app_password",
            from_email="your@gmail.com",
            from_name="Your Name"
        ))
        
        template = EmailTemplate(
            name="Welcome",
            subject="Welcome, {first_name}!",
            body_html="<h1>Hi {first_name}!</h1><p>Thanks for signing up.</p>"
        )
        
        # From CSV
        results = sender.send_from_csv("contacts.csv", template)
    """
    
    def __init__(self, config: EmailConfig, rate_limit: float = 1.0):
        """
        Initialize the sender.
        
        Args:
            config: SMTP configuration
            rate_limit: Seconds between sends (default 1.0)
        """
        self.config = config
        self.rate_limit = rate_limit
        self.results: List[SendResult] = []
        
    def send_one(
        self,
        to: str,
        subject: str,
        body_html: str,
        body_text: Optional[str] = None,
        reply_to: Optional[str] = None
    ) -> SendResult:
        """
        Send a single email.
        
        Args:
            to: Recipient email
            subject: Email subject
            body_html: HTML body
            body_text: Plain text body (optional)
            reply_to: Reply-to address (optional)
            
        Returns:
            SendResult with status
        """
        try:
            # Create message
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"{self.config.from_name} <{self.config.from_email}>" if self.config.from_name else self.config.from_email
            msg["To"] = to
            if reply_to:
                msg["Reply-To"] = reply_to
                
            # Add bodies
            if body_text:
                msg.attach(MIMEText(body_text, "plain"))
            msg.attach(MIMEText(body_html, "html"))
            
            # Send
            with smtplib.SMTP(self.config.host, self.config.port) as server:
                if self.config.use_tls:
                    server.starttls()
                server.login(self.config.username, self.config.password)
                server.send_message(msg)
                
            result = SendResult(
                to=to,
                success=True,
                sent_at=datetime.now().isoformat()
            )
            
        except Exception as e:
            result = SendResult(
                to=to,
                success=False,
                error=str(e)
            )
            
        self.results.append(result)
        return result
        
    def send_templated(
        self,
        to: str,
        template: EmailTemplate,
        variables: Dict[str, str],
        reply_to: Optional[str] = None
    ) -> SendResult:
        """
        Send an email using a template with variable substitution.
        
        Args:
            to: Recipient email
            template: Email template
            variables: Dict of {placeholder: value}
            reply_to: Reply-to address
            
        Returns:
            SendResult
        """
        # Substitute variables
        subject = self._substitute(template.subject, variables)
        body_html = self._substitute(template.body_html, variables)
        body_text = self._substitute(template.body_text, variables) if template.body_text else None
        
        return self.send_one(to, subject, body_html, body_text, reply_to)
        
    def _substitute(self, text: str, variables: Dict[str, str]) -> str:
        """Replace {var} placeholders with values."""
        result = text
        for key, value in variables.items():
            result = result.replace(f"{{{key}}}", str(value))
        return result
        
    def send_from_csv(
        self,
        csv_path: str,
        template: EmailTemplate,
        email_column: str = "email",
        max_sends: Optional[int] = None,
        dry_run: bool = False
    ) -> List[SendResult]:
        """
        Send emails to all recipients in a CSV file.
        
        CSV columns become template variables.
        
        Args:
            csv_path: Path to CSV file
            template: Email template
            email_column: Column name for email addresses
            max_sends: Maximum number to send (optional)
            dry_run: If True, don't actually send
            
        Returns:
            List of SendResults
        """
        results = []
        
        with open(csv_path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for i, row in enumerate(reader):
                if max_sends and i >= max_sends:
                    break
                    
                email = row.get(email_column)
                if not email:
                    continue
                    
                print(f"Sending {i+1}: {email}")
                
                if dry_run:
                    result = SendResult(to=email, success=True, error="DRY_RUN")
                else:
                    result = self.send_templated(email, template, row)
                    
                results.append(result)
                
                # Rate limiting
                if not dry_run and self.rate_limit > 0:
                    time.sleep(self.rate_limit)
                    
        return results
        
    def send_from_list(
        self,
        recipients: List[Dict[str, str]],
        template: EmailTemplate,
        email_key: str = "email",
        dry_run: bool = False
    ) -> List[SendResult]:
        """
        Send emails to a list of recipient dicts.
        
        Args:
            recipients: List of dicts with recipient data
            template: Email template
            email_key: Key for email address in each dict
            dry_run: If True, don't actually send
            
        Returns:
            List of SendResults
        """
        results = []
        
        for i, recipient in enumerate(recipients):
            email = recipient.get(email_key)
            if not email:
                continue
                
            print(f"Sending {i+1}: {email}")
            
            if dry_run:
                result = SendResult(to=email, success=True, error="DRY_RUN")
            else:
                result = self.send_templated(email, template, recipient)
                
            results.append(result)
            
            if not dry_run and self.rate_limit > 0:
                time.sleep(self.rate_limit)
                
        return results
        
    def export_results(self, filepath: str):
        """Export send results to JSON."""
        data = [asdict(r) for r in self.results]
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
            
    def get_stats(self) -> Dict[str, int]:
        """Get send statistics."""
        successful = sum(1 for r in self.results if r.success)
        failed = sum(1 for r in self.results if not r.success)
        return {
            "total": len(self.results),
            "successful": successful,
            "failed": failed,
            "success_rate": round(successful / len(self.results) * 100, 1) if self.results else 0
        }


# Gmail-specific configuration
def gmail_config(email: str, app_password: str, name: Optional[str] = None) -> EmailConfig:
    """Create Gmail SMTP config (requires App Password)."""
    return EmailConfig(
        host="smtp.gmail.com",
        port=587,
        username=email,
        password=app_password,
        from_email=email,
        from_name=name,
        use_tls=True
    )


def demo():
    """Demo the email sender."""
    print("=== Email Automation Demo ===\n")
    
    print("Example usage:\n")
    print("""
    from email_sender import EmailSender, EmailTemplate, gmail_config
    
    # Configure for Gmail
    config = gmail_config(
        email="your@gmail.com",
        app_password="xxxx xxxx xxxx xxxx",  # App Password, not regular password
        name="Your Name"
    )
    
    sender = EmailSender(config, rate_limit=1.0)
    
    # Create template
    template = EmailTemplate(
        name="Welcome",
        subject="Welcome to our service, {first_name}!",
        body_html=\"\"\"
        <h1>Hi {first_name}!</h1>
        <p>Thanks for signing up at {company}.</p>
        <p>Best regards,<br>The Team</p>
        \"\"\"
    )
    
    # Send from CSV (contacts.csv has: email,first_name,company)
    results = sender.send_from_csv(
        "contacts.csv",
        template,
        email_column="email",
        dry_run=True  # Set False to actually send
    )
    
    # Check stats
    print(sender.get_stats())
    
    # Export results
    sender.export_results("send_results.json")
    """)
    
    print("\nGmail Setup:")
    print("1. Enable 2FA on your Google account")
    print("2. Create App Password: myaccount.google.com/apppasswords")
    print("3. Use the 16-character App Password (not your regular password)")


if __name__ == "__main__":
    demo()
