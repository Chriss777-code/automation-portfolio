# PDF Data Extractor 📄

**Extract tables, text, and structured data from PDFs**

Transform PDF documents into usable data formats (CSV, JSON, Google Sheets).

## Features

- 📊 Table extraction with headers preserved
- 📝 Full text extraction
- 🔍 Smart field detection (invoices, receipts)
- 📦 Batch processing
- 📤 Multiple export formats

## Quick Start

```python
from pdf_extractor import PDFExtractor

# Extract everything
extractor = PDFExtractor()
result = extractor.extract("invoice.pdf")

# Access the data
print(f"Pages: {result.page_count}")
print(f"Tables found: {len(result.tables)}")

for table in result.tables:
    print(f"Table on page {table.page_number}: {len(table.rows)} rows")
    print(f"Headers: {table.headers}")

# Export to CSV
extractor.to_csv(result, "output.csv")

# Export to JSON
extractor.to_json(result, "output.json")
```

## Smart Invoice Extraction

```python
from pdf_extractor import PDFExtractor, extract_invoice_fields

extractor = PDFExtractor()
result = extractor.extract("invoice.pdf")

fields = extract_invoice_fields(result)
print(f"Invoice #: {fields.get('invoice_number')}")
print(f"Date: {fields.get('date')}")
print(f"Total: {fields.get('total')}")
print(f"Email: {fields.get('email')}")
```

## Batch Processing

```python
pdfs = ["invoice1.pdf", "invoice2.pdf", "invoice3.pdf"]
results = extractor.extract_batch(pdfs, output_dir="./extracted/")
```

## Google Sheets Integration

```python
# Get data formatted for Google Sheets API
sheets_data = extractor.tables_to_sheets_format(result)

# Ready for batchUpdate call
for sheet in sheets_data:
    print(f"Range: {sheet['range']}")
    print(f"Rows: {len(sheet['values'])}")
```

## Data Structure

```python
ExtractionResult:
    filepath: str           # Original PDF path
    filename: str           # PDF filename
    page_count: int         # Number of pages
    tables: List[ExtractedTable]
    text_pages: List[ExtractedText]
    metadata: Dict          # PDF metadata
    extracted_at: str       # Timestamp

ExtractedTable:
    page_number: int
    table_index: int
    headers: List[str]
    rows: List[List[str]]
    raw_data: List[List[Any]]

ExtractedText:
    page_number: int
    text: str
    word_count: int
```

## Requirements

```bash
# Recommended (best table support)
pip install pdfplumber

# Alternative (text only)
pip install pypdf

# Optional (alternative table extraction)
pip install tabula-py
```

## Supported PDF Types

| Type | Support |
|------|---------|
| Digital PDFs | ✅ Full |
| Scanned PDFs | ⚠️ Limited (OCR needed) |
| Password-protected | ❌ Not yet |
| Encrypted | ❌ Not yet |

## Common Use Cases

### Invoice Processing
Extract invoice numbers, dates, line items, and totals.

### Bank Statements
Extract transaction tables with dates, descriptions, amounts.

### Reports
Extract data tables from reports for analysis.

### Forms
Extract filled form fields (with pattern matching).

## Error Handling

```python
try:
    result = extractor.extract("file.pdf")
except FileNotFoundError:
    print("PDF not found")
except Exception as e:
    print(f"Extraction error: {e}")
```

## Author

Built by Neo (AI Assistant) for Upwork automation portfolio.

## License

MIT
