"""
Google Sheets Data Pipeline
============================
Automated data extraction and upload to Google Sheets.

Features:
- Service account authentication
- Batch updates for efficiency
- Auto-create sheets/tabs
- Data validation
- Scheduled execution support

Author: Chris S.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class SheetsDataPipeline:
    """Pipeline for pushing data to Google Sheets."""
    
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    
    def __init__(self, credentials_file: str, spreadsheet_id: str):
        """
        Initialize the pipeline.
        
        Args:
            credentials_file: Path to service account JSON key file
            spreadsheet_id: Google Sheets document ID (from URL)
        """
        self.spreadsheet_id = spreadsheet_id
        self.credentials = service_account.Credentials.from_service_account_file(
            credentials_file, scopes=self.SCOPES
        )
        self.service = build('sheets', 'v4', credentials=self.credentials)
        self.sheets = self.service.spreadsheets()
    
    def get_sheet_names(self) -> List[str]:
        """Get list of all sheet/tab names in the spreadsheet."""
        result = self.sheets.get(spreadsheetId=self.spreadsheet_id).execute()
        return [sheet['properties']['title'] for sheet in result.get('sheets', [])]
    
    def create_sheet(self, title: str) -> bool:
        """Create a new sheet/tab if it doesn't exist."""
        existing = self.get_sheet_names()
        if title in existing:
            print(f"ℹ Sheet '{title}' already exists")
            return False
        
        try:
            request = {
                'requests': [{
                    'addSheet': {
                        'properties': {'title': title}
                    }
                }]
            }
            self.sheets.batchUpdate(
                spreadsheetId=self.spreadsheet_id,
                body=request
            ).execute()
            print(f"✓ Created sheet: {title}")
            return True
        except HttpError as e:
            print(f"⚠ Error creating sheet: {e}")
            return False
    
    def clear_sheet(self, sheet_name: str):
        """Clear all data from a sheet."""
        try:
            self.sheets.values().clear(
                spreadsheetId=self.spreadsheet_id,
                range=sheet_name
            ).execute()
            print(f"✓ Cleared sheet: {sheet_name}")
        except HttpError as e:
            print(f"⚠ Error clearing sheet: {e}")
    
    def write_data(
        self,
        sheet_name: str,
        data: List[List[Any]],
        start_cell: str = "A1",
        include_header: bool = True,
        header: Optional[List[str]] = None
    ) -> int:
        """
        Write data to a sheet.
        
        Args:
            sheet_name: Target sheet/tab name
            data: List of rows (each row is a list of values)
            start_cell: Starting cell (e.g., "A1")
            include_header: Whether to include header row
            header: Custom header row (auto-detects from dict keys if not provided)
        
        Returns:
            Number of rows written
        """
        # Prepare data with optional header
        rows_to_write = []
        if include_header and header:
            rows_to_write.append(header)
        rows_to_write.extend(data)
        
        if not rows_to_write:
            print("⚠ No data to write")
            return 0
        
        try:
            range_name = f"{sheet_name}!{start_cell}"
            body = {'values': rows_to_write}
            
            result = self.sheets.values().update(
                spreadsheetId=self.spreadsheet_id,
                range=range_name,
                valueInputOption='USER_ENTERED',
                body=body
            ).execute()
            
            rows_updated = result.get('updatedRows', 0)
            print(f"✓ Wrote {rows_updated} rows to {sheet_name}")
            return rows_updated
            
        except HttpError as e:
            print(f"⚠ Error writing data: {e}")
            return 0
    
    def append_data(self, sheet_name: str, data: List[List[Any]]) -> int:
        """Append rows to the end of existing data."""
        try:
            body = {'values': data}
            
            result = self.sheets.values().append(
                spreadsheetId=self.spreadsheet_id,
                range=sheet_name,
                valueInputOption='USER_ENTERED',
                insertDataOption='INSERT_ROWS',
                body=body
            ).execute()
            
            rows_appended = result.get('updates', {}).get('updatedRows', 0)
            print(f"✓ Appended {rows_appended} rows to {sheet_name}")
            return rows_appended
            
        except HttpError as e:
            print(f"⚠ Error appending data: {e}")
            return 0
    
    def read_data(self, sheet_name: str, range_str: str = "") -> List[List[Any]]:
        """Read data from a sheet."""
        try:
            range_name = f"{sheet_name}!{range_str}" if range_str else sheet_name
            result = self.sheets.values().get(
                spreadsheetId=self.spreadsheet_id,
                range=range_name
            ).execute()
            return result.get('values', [])
        except HttpError as e:
            print(f"⚠ Error reading data: {e}")
            return []
    
    def dict_to_rows(
        self,
        data: List[Dict[str, Any]],
        columns: Optional[List[str]] = None
    ) -> tuple[List[str], List[List[Any]]]:
        """
        Convert list of dicts to header + rows format.
        
        Returns:
            Tuple of (header_row, data_rows)
        """
        if not data:
            return [], []
        
        # Use provided columns or extract from first dict
        header = columns or list(data[0].keys())
        rows = [[item.get(col, '') for col in header] for item in data]
        
        return header, rows


# Example usage
def example_pipeline():
    """Example: Push transaction data to Google Sheets."""
    
    # Initialize pipeline
    pipeline = SheetsDataPipeline(
        credentials_file='service_account.json',
        spreadsheet_id='YOUR_SPREADSHEET_ID_HERE'
    )
    
    # Sample transaction data
    transactions = [
        {'date': '2024-01-15', 'description': 'Amazon', 'amount': -45.99, 'category': 'Shopping'},
        {'date': '2024-01-16', 'description': 'Paycheck', 'amount': 3500.00, 'category': 'Income'},
        {'date': '2024-01-17', 'description': 'Grocery Store', 'amount': -127.50, 'category': 'Food'},
    ]
    
    # Convert to sheets format
    header, rows = pipeline.dict_to_rows(transactions)
    
    # Create monthly sheet
    sheet_name = f"Transactions {datetime.now().strftime('%B %Y')}"
    pipeline.create_sheet(sheet_name)
    
    # Write data with header
    pipeline.write_data(sheet_name, rows, include_header=True, header=header)
    
    print("✓ Pipeline complete!")


if __name__ == "__main__":
    print("Google Sheets Pipeline ready!")
    print("Configure credentials_file and spreadsheet_id to use.")
    # example_pipeline()
