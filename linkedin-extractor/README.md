# LinkedIn Profile Extractor 👔

**Stealth data extraction from LinkedIn profiles**

Extract structured data from LinkedIn profiles with anti-detection and session persistence.

⚠️ **Disclaimer:** Use responsibly. Respect LinkedIn's Terms of Service and rate limits. This is for educational purposes.

## Features

- 🥷 Stealth mode (anti-detection scripts)
- 🔐 Session persistence (stay logged in)
- 📊 Structured data output
- ⏱️ Built-in rate limiting
- 📤 Export to JSON/CSV

## Quick Start

```python
from linkedin_extractor import LinkedInExtractor
import asyncio

async def main():
    async with LinkedInExtractor(headless=False) as extractor:
        # First run: Manual login required
        await extractor.login_manual()
        
        # Check if logged in
        if await extractor.is_logged_in():
            print("✅ Logged in!")
            
            # Extract a profile
            profile = await extractor.extract_profile(
                "https://www.linkedin.com/in/satyanadella/"
            )
            
            print(f"Name: {profile.name}")
            print(f"Headline: {profile.headline}")
            print(f"Company: {profile.current_company}")

asyncio.run(main())
```

## Data Extracted

| Field | Type | Description |
|-------|------|-------------|
| `name` | str | Full name |
| `headline` | str | Profile headline |
| `location` | str | Location |
| `about` | str | About section |
| `current_title` | str | Current job title |
| `current_company` | str | Current employer |
| `connections` | str | Connection count |
| `experience` | List[Dict] | Work history |
| `education` | List[Dict] | Education history |
| `skills` | List[str] | Skills list |

## Session Persistence

After first login, cookies are saved to `linkedin_session/cookies.json`.
Subsequent runs load the session automatically.

```python
# First run - opens browser, wait for manual login
await extractor.login_manual()

# Future runs - auto-loads session
if await extractor.is_logged_in():
    # Already logged in, extract profiles
    ...
```

## Multiple Profiles

```python
urls = [
    "https://linkedin.com/in/person1",
    "https://linkedin.com/in/person2",
]

profiles = await extractor.extract_multiple(
    urls,
    delay_seconds=(5, 10)  # Random delay between profiles
)
```

## Export Options

```python
from linkedin_extractor import export_to_json, export_to_csv

# JSON (full data)
export_to_json(profiles, "profiles.json")

# CSV (flattened)
export_to_csv(profiles, "profiles.csv")
```

## Rate Limiting Guidelines

LinkedIn is strict about automation. Recommended limits:

| Action | Safe Rate |
|--------|-----------|
| Profile views | 30/hour |
| Delay between profiles | 5-15 seconds |
| Daily limit | 100-150 profiles |

## Configuration

```python
extractor = LinkedInExtractor(
    session_dir="./my_session",  # Where to store cookies
    headless=False,              # Show browser (recommended)
    slow_mode=100,               # ms between actions
)
```

## Requirements

```
playwright>=1.40.0
```

## Troubleshooting

### "Not logged in" after restart
- Delete `linkedin_session/cookies.json`
- Run `login_manual()` again

### Blocked or CAPTCHA
- Use `headless=False` 
- Increase delays
- Reduce volume
- Consider using your real account's session

### Missing data
- LinkedIn frequently changes their HTML structure
- Selectors may need updating
- Check element inspection in browser

## Author

Built by Neo (AI Assistant) for Upwork automation portfolio.

## License

MIT - Use responsibly.
