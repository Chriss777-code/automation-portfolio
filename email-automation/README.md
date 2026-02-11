# Email Automation 📧

**Bulk email sending with templates and CSV support**

Send personalized emails at scale with variable substitution and rate limiting.

## Features

- 📝 Template-based emails with {variable} placeholders
- 📊 CSV data source for bulk sends
- ⏱️ Built-in rate limiting
- 📈 Send tracking and statistics
- 🔄 Dry run mode for testing
- 📤 Gmail ready (SMTP)

## Quick Start

```python
from email_sender import EmailSender, EmailTemplate, gmail_config

# Configure for Gmail
config = gmail_config(
    email="your@gmail.com",
    app_password="xxxx xxxx xxxx xxxx",  # App Password
    name="Your Name"
)

sender = EmailSender(config, rate_limit=1.0)

# Create template
template = EmailTemplate(
    name="Welcome",
    subject="Welcome, {first_name}!",
    body_html="""
    <h1>Hi {first_name}!</h1>
    <p>Thanks for signing up.</p>
    """
)

# Send from CSV
results = sender.send_from_csv("contacts.csv", template)
print(sender.get_stats())
```

## CSV Format

```csv
email,first_name,last_name,company
john@example.com,John,Smith,Acme Inc
jane@example.com,Jane,Doe,Tech Corp
```

Any column can be used as a template variable: `{first_name}`, `{company}`, etc.

## Template Variables

```python
template = EmailTemplate(
    name="Newsletter",
    subject="{company} Weekly Update - {date}",
    body_html="""
    <h1>Hi {first_name}!</h1>
    <p>Here's your weekly update for {company}...</p>
    """,
    body_text="Hi {first_name}! Here's your weekly update..."  # Optional plain text
)
```

## Rate Limiting

```python
# 1 email per second (default)
sender = EmailSender(config, rate_limit=1.0)

# 2 emails per second
sender = EmailSender(config, rate_limit=0.5)

# No rate limiting (careful!)
sender = EmailSender(config, rate_limit=0)
```

## Dry Run Mode

Test without sending:
```python
results = sender.send_from_csv("contacts.csv", template, dry_run=True)
```

## Send Limits

```python
# Only send first 10
results = sender.send_from_csv("contacts.csv", template, max_sends=10)
```

## Results Tracking

```python
# Get statistics
stats = sender.get_stats()
# {"total": 100, "successful": 98, "failed": 2, "success_rate": 98.0}

# Export to JSON
sender.export_results("results.json")
```

## Gmail Setup

1. Enable 2-Factor Authentication on Google account
2. Go to: myaccount.google.com/apppasswords
3. Generate an App Password
4. Use the 16-character password (not your regular password)

```python
config = gmail_config(
    email="your@gmail.com",
    app_password="abcd efgh ijkl mnop",
    name="Your Name"
)
```

## Other SMTP Providers

```python
from email_sender import EmailSender, EmailConfig

config = EmailConfig(
    host="smtp.provider.com",
    port=587,
    username="user@provider.com",
    password="password",
    from_email="user@provider.com",
    from_name="Your Name",
    use_tls=True
)
```

## Requirements

```
# No external dependencies - uses Python stdlib
```

## Best Practices

1. **Always test with dry_run=True first**
2. **Use rate limiting to avoid being flagged as spam**
3. **Include unsubscribe link in bulk emails**
4. **Respect CAN-SPAM and GDPR regulations**
5. **Don't send unsolicited bulk email**

## Author

Built by Neo (AI Assistant) for Upwork automation portfolio.

## License

MIT
