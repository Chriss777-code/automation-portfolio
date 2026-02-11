# X (Twitter) Stealth Automation 🐦

**Stealth posting and engagement for X/Twitter using DrissionPage**

Avoid bot detection with session persistence and human-like behavior.

⚠️ **Disclaimer:** Use responsibly. Respect X's Terms of Service. Educational purposes only.

## Features

- 🥷 Stealth mode (anti-detection)
- 🔐 Session persistence (login once, use forever)
- ⏱️ Human-like delays
- 📝 Post tweets
- ❤️ Like tweets
- 💬 Reply to tweets
- ➕ Follow users

## Quick Start

```python
from x_stealth_poster import XStealthClient, Tweet

# First time: Manual login (visible browser)
client = XStealthClient(session_name="my_account", headless=False)
client.start()
client.manual_login()  # Log in manually, session saved automatically

# Later: Use saved session (can run headless)
client = XStealthClient(session_name="my_account", headless=True)
client.load_session()

if client.is_logged_in():
    # Post a tweet
    client.post_tweet(Tweet(text="Hello world!"))
    
    # Engage
    client.like_tweet("https://x.com/user/status/123...")
    client.reply_to_tweet("https://x.com/user/status/123...", "Great post!")
    client.follow_user("elonmusk")

client.close()
```

## Session Persistence

Sessions are stored in `~/.clawdbot/browser-sessions/`:
- `{session_name}_cookies.json` - Browser cookies
- `{session_name}_storage.json` - localStorage data

Once logged in, you can run headless without re-authenticating.

## Anti-Detection Features

1. **Disabled automation flags** - `AutomationControlled` disabled
2. **Realistic User-Agent** - Chrome 120 on Windows
3. **Human-like typing** - Random delays between keystrokes
4. **Random delays** - 0.5-2s between actions
5. **DrissionPage** - Native Python, no Selenium markers

## Rate Limiting Guidelines

X is aggressive about bot detection. Recommended limits:

| Action | Safe Rate |
|--------|-----------|
| Tweets | 5-10/day |
| Likes | 20-50/day |
| Follows | 10-20/day |
| Replies | 10-30/day |

Always use `slow_mode=True` (default).

## Configuration

```python
client = XStealthClient(
    session_name="my_account",  # Unique session name
    headless=False,             # False for login, True later
    slow_mode=True,             # Random delays (recommended)
)
```

## Requirements

```bash
pip install DrissionPage
```

## Testing

Before using on a real account, test stealth:
```bash
python -c "from DrissionPage import ChromiumPage; p=ChromiumPage(); p.get('https://bot.sannysoft.com'); print(p.title)"
```

Should output "Antibot" without detection warnings.

## Troubleshooting

### Login not detected
- Make sure you're fully logged in (see home feed)
- Wait for redirect to complete

### Session not loading
- Delete old session files and re-login
- Check cookies are valid (not expired)

### Bot detection triggered
- Reduce action frequency
- Use residential proxy
- Add longer delays
- Login manually again

## Author

Built by Neo (AI Assistant) for Upwork automation portfolio.

## License

MIT - Use responsibly.
