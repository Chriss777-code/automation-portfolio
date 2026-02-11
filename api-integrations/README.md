# API Integrations 🔌

**Connect services with clean, maintainable code**

Templates for common API integration patterns.

## Available Integrations

### Airtable ↔️ Google Sheets Sync
**File:** `airtable_sheets_sync.py`

Bidirectional sync between Airtable and Google Sheets.

**Features:**
- One-way or two-way sync
- Custom field mapping
- Key-based record matching
- Incremental updates

```python
from airtable_sheets_sync import AirtableSheetsSync, SyncConfig

sync = AirtableSheetsSync(
    airtable_key="pat...",
    sheets_credentials="service_account.json"
)

config = SyncConfig(
    airtable_base_id="appXXX",
    airtable_table_name="Contacts",
    sheets_id="1abc...",
    sheets_range="Contacts!A:F",
    key_field="Email",
    field_mapping={
        "Name": "A",
        "Email": "B",
        "Phone": "C"
    },
    sync_direction="airtable_to_sheets"
)

result = sync.sync(config)
```

## Common Integration Patterns

### 1. CRM to Spreadsheet
Sync leads/contacts from CRM to spreadsheets for reporting.

### 2. Form to Database
Push form submissions (Typeform, JotForm) to Airtable/Notion.

### 3. Notification Pipeline
Connect multiple services to a single notification channel.

### 4. Data Backup
Scheduled exports from web apps to spreadsheets/databases.

## Adding New Integrations

Each integration should include:
- API client class with authentication
- Sync/transfer logic
- Configuration dataclass
- Result tracking
- Error handling

## Requirements

```
requests>=2.28.0
google-auth>=2.0.0
google-api-python-client>=2.0.0
```

## Environment Variables

```bash
AIRTABLE_API_KEY=pat...
GOOGLE_APPLICATION_CREDENTIALS=service_account.json
```

## Author

Built by Neo (AI Assistant) for Upwork automation portfolio.

## License

MIT
