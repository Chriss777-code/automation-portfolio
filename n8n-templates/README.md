# n8n Workflow Templates 🔄

**Ready-to-import automation workflows for n8n**

These templates can be imported directly into n8n. Just replace the placeholder values (YOUR_SHEET_ID, YOUR_CHAT_ID, etc.) with your actual credentials.

## Templates

### 1. Lead Notification Workflow
**File:** `lead_notification_workflow.json`

Monitors a Google Sheet for new leads and sends instant notifications.

**Features:**
- ⏰ Checks every 5 minutes (configurable)
- 📊 Reads from Google Sheets
- 🔔 Sends to Telegram + Slack
- ✅ Marks leads as "Notified" to avoid duplicates

**Setup:**
1. Import JSON into n8n
2. Replace `YOUR_SHEET_ID` with your Google Sheet ID
3. Replace `YOUR_CHAT_ID` with your Telegram chat ID
4. Connect your Google + Telegram credentials in n8n
5. Activate the workflow

### 2. Content Aggregator (Coming Soon)
Aggregate content from multiple RSS feeds → summarize with AI → post to social.

### 3. CRM Sync (Coming Soon)
Sync contacts between Google Sheets and HubSpot/Salesforce.

## How to Import

1. Open n8n
2. Click "Import from File"
3. Select the `.json` file
4. Configure credentials
5. Activate

## Requirements

- n8n (self-hosted or cloud)
- Google Sheets API credentials
- Telegram bot token
- (Optional) Slack webhook

## Customization

All templates are starting points. Common modifications:

- **Change trigger frequency:** Edit the Schedule Trigger node
- **Add more notification channels:** Duplicate and modify the notification nodes
- **Change data source:** Replace Google Sheets with Airtable, Notion, etc.
- **Add AI processing:** Insert an OpenAI node between source and notification

## Author

Built by Neo (AI Assistant) as part of an overnight automation portfolio build.

## License

MIT - Use freely, modify as needed.
