# Google Sheets Integration

Automated data pipeline for pushing data to Google Sheets via API.

## Features

- ✅ Service account authentication
- ✅ Batch read/write operations
- ✅ Auto-create sheets/tabs
- ✅ Append or overwrite modes
- ✅ Dict-to-rows conversion

## Setup

### 1. Create Service Account

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create project → Enable Sheets API
3. Create Service Account → Download JSON key
4. Share your spreadsheet with the service account email

### 2. Install Dependencies

```bash
pip install google-auth google-auth-oauthlib google-api-python-client
```

## Quick Start

```python
from sheets_pipeline import SheetsDataPipeline

pipeline = SheetsDataPipeline(
    credentials_file='service_account.json',
    spreadsheet_id='1ABC...'  # From sheet URL
)

# Write data
data = [
    ['Name', 'Email', 'Status'],
    ['John', 'john@example.com', 'Active'],
    ['Jane', 'jane@example.com', 'Pending'],
]
pipeline.write_data('Sheet1', data)

# Append rows
new_rows = [['Bob', 'bob@example.com', 'Active']]
pipeline.append_data('Sheet1', new_rows)

# Read data
existing = pipeline.read_data('Sheet1')
```

## Use Cases

- Financial data dashboards
- Automated reporting
- Data collection pipelines
- CRM data sync
- Inventory tracking

## License

MIT
