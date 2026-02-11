#!/usr/bin/env python3
"""
PDF Data Extractor - Extract structured data from PDFs

This tool extracts tables, text, and structured data from PDF documents
and outputs to CSV, JSON, or Google Sheets format.

Features:
- Table extraction with formatting preserved
- OCR for scanned documents (optional)
- Batch processing
- Multiple output formats
- Smart field detection

Author: Neo (AI Assistant)
Date: 2026-02-11
"""

import json
import re
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any, Union
from dataclasses import dataclass, asdict

# Core PDF libraries (install separately)
try:
    import pdfplumber
    HAS_PDFPLUMBER = True
except ImportError:
    HAS_PDFPLUMBER = False

try:
    from pypdf import PdfReader
    HAS_PYPDF = True
except ImportError:
    HAS_PYPDF = False

try:
    import tabula
    HAS_TABULA = True
except ImportError:
    HAS_TABULA = False


@dataclass
class ExtractedTable:
    """A table extracted from a PDF."""
    page_number: int
    table_index: int
    headers: List[str]
    rows: List[List[str]]
    raw_data: List[List[Any]]


@dataclass
class ExtractedText:
    """Text extracted from a PDF page."""
    page_number: int
    text: str
    word_count: int


@dataclass
class ExtractionResult:
    """Complete extraction result from a PDF."""
    filepath: str
    filename: str
    page_count: int
    tables: List[ExtractedTable]
    text_pages: List[ExtractedText]
    metadata: Dict[str, Any]
    extracted_at: str


class PDFExtractor:
    """
    Extract structured data from PDF files.
    
    Usage:
        extractor = PDFExtractor()
        result = extractor.extract("invoice.pdf")
        
        # Export
        extractor.to_csv(result, "output.csv")
        extractor.to_json(result, "output.json")
    """
    
    def __init__(
        self,
        extract_tables: bool = True,
        extract_text: bool = True,
        use_ocr: bool = False,
    ):
        """
        Initialize the extractor.
        
        Args:
            extract_tables: Extract table data
            extract_text: Extract raw text
            use_ocr: Use OCR for scanned documents (requires pytesseract)
        """
        self.extract_tables = extract_tables
        self.extract_text = extract_text
        self.use_ocr = use_ocr
        
        # Check available libraries
        if not HAS_PDFPLUMBER and not HAS_PYPDF:
            raise ImportError(
                "No PDF library found. Install pdfplumber or pypdf:\n"
                "pip install pdfplumber  # recommended\n"
                "pip install pypdf"
            )
            
    def extract(self, filepath: Union[str, Path]) -> ExtractionResult:
        """
        Extract all data from a PDF file.
        
        Args:
            filepath: Path to PDF file
            
        Returns:
            ExtractionResult with tables, text, and metadata
        """
        filepath = Path(filepath)
        
        if not filepath.exists():
            raise FileNotFoundError(f"PDF not found: {filepath}")
            
        tables = []
        text_pages = []
        metadata = {}
        page_count = 0
        
        if HAS_PDFPLUMBER:
            # Use pdfplumber (best for tables)
            with pdfplumber.open(filepath) as pdf:
                page_count = len(pdf.pages)
                metadata = pdf.metadata or {}
                
                for page_num, page in enumerate(pdf.pages, 1):
                    # Extract tables
                    if self.extract_tables:
                        page_tables = page.extract_tables()
                        for table_idx, table_data in enumerate(page_tables):
                            if table_data and len(table_data) > 1:
                                # First row as headers
                                headers = [str(h) if h else "" for h in table_data[0]]
                                rows = [
                                    [str(c) if c else "" for c in row]
                                    for row in table_data[1:]
                                ]
                                
                                tables.append(ExtractedTable(
                                    page_number=page_num,
                                    table_index=table_idx,
                                    headers=headers,
                                    rows=rows,
                                    raw_data=table_data
                                ))
                                
                    # Extract text
                    if self.extract_text:
                        text = page.extract_text() or ""
                        text_pages.append(ExtractedText(
                            page_number=page_num,
                            text=text,
                            word_count=len(text.split())
                        ))
                        
        elif HAS_PYPDF:
            # Fallback to pypdf (text only)
            reader = PdfReader(str(filepath))
            page_count = len(reader.pages)
            metadata = dict(reader.metadata) if reader.metadata else {}
            
            for page_num, page in enumerate(reader.pages, 1):
                if self.extract_text:
                    text = page.extract_text() or ""
                    text_pages.append(ExtractedText(
                        page_number=page_num,
                        text=text,
                        word_count=len(text.split())
                    ))
                    
            if self.extract_tables:
                print("Warning: pypdf doesn't support table extraction. Install pdfplumber.")
                
        return ExtractionResult(
            filepath=str(filepath),
            filename=filepath.name,
            page_count=page_count,
            tables=tables,
            text_pages=text_pages,
            metadata=metadata,
            extracted_at=datetime.now().isoformat()
        )
        
    def extract_batch(
        self,
        filepaths: List[Union[str, Path]],
        output_dir: Optional[str] = None
    ) -> List[ExtractionResult]:
        """
        Extract from multiple PDFs.
        
        Args:
            filepaths: List of PDF paths
            output_dir: Optional directory for individual outputs
        """
        results = []
        
        for filepath in filepaths:
            print(f"Processing: {filepath}")
            try:
                result = self.extract(filepath)
                results.append(result)
                
                if output_dir:
                    output_path = Path(output_dir) / f"{Path(filepath).stem}.json"
                    self.to_json(result, output_path)
                    
            except Exception as e:
                print(f"Error processing {filepath}: {e}")
                
        return results
        
    def to_csv(self, result: ExtractionResult, filepath: str, table_index: int = 0):
        """
        Export a specific table to CSV.
        
        Args:
            result: Extraction result
            filepath: Output CSV path
            table_index: Which table to export (default: first)
        """
        import csv
        
        if not result.tables:
            raise ValueError("No tables found in extraction result")
            
        if table_index >= len(result.tables):
            raise ValueError(f"Table index {table_index} out of range")
            
        table = result.tables[table_index]
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(table.headers)
            writer.writerows(table.rows)
            
    def to_json(self, result: ExtractionResult, filepath: str):
        """Export extraction result to JSON."""
        data = {
            "filepath": result.filepath,
            "filename": result.filename,
            "page_count": result.page_count,
            "metadata": result.metadata,
            "extracted_at": result.extracted_at,
            "tables": [asdict(t) for t in result.tables],
            "text_pages": [asdict(t) for t in result.text_pages],
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)
            
    def tables_to_sheets_format(self, result: ExtractionResult) -> List[Dict]:
        """
        Convert tables to Google Sheets API format.
        
        Returns list of dicts with 'range' and 'values' for batchUpdate.
        """
        sheets_data = []
        
        for table in result.tables:
            all_rows = [table.headers] + table.rows
            sheets_data.append({
                "range": f"Page{table.page_number}_Table{table.table_index}!A1",
                "values": all_rows
            })
            
        return sheets_data


def extract_invoice_fields(result: ExtractionResult) -> Dict[str, Any]:
    """
    Smart extraction for common invoice fields.
    
    Looks for common patterns like invoice numbers, dates, totals.
    """
    all_text = " ".join(page.text for page in result.text_pages)
    
    fields = {}
    
    # Invoice number patterns
    invoice_match = re.search(
        r'(?:invoice|inv|invoice\s*#|invoice\s*no\.?)\s*[:\s]*([A-Z0-9-]+)',
        all_text,
        re.IGNORECASE
    )
    if invoice_match:
        fields["invoice_number"] = invoice_match.group(1)
        
    # Date patterns
    date_match = re.search(
        r'(?:date|invoice\s*date)[:\s]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\w+\s+\d{1,2},?\s+\d{4})',
        all_text,
        re.IGNORECASE
    )
    if date_match:
        fields["date"] = date_match.group(1)
        
    # Total amount patterns
    total_match = re.search(
        r'(?:total|amount\s*due|grand\s*total)[:\s]*\$?([\d,]+\.?\d*)',
        all_text,
        re.IGNORECASE
    )
    if total_match:
        fields["total"] = total_match.group(1)
        
    # Email pattern
    email_match = re.search(r'[\w.-]+@[\w.-]+\.\w+', all_text)
    if email_match:
        fields["email"] = email_match.group()
        
    return fields


def demo():
    """Demo the PDF extractor."""
    print("=== PDF Extractor Demo ===\n")
    
    if not HAS_PDFPLUMBER and not HAS_PYPDF:
        print("Error: No PDF library installed.")
        print("Install: pip install pdfplumber")
        return
        
    print("Available features:")
    print(f"  - pdfplumber (tables + text): {'✅' if HAS_PDFPLUMBER else '❌'}")
    print(f"  - pypdf (text only): {'✅' if HAS_PYPDF else '❌'}")
    print(f"  - tabula (alternative tables): {'✅' if HAS_TABULA else '❌'}")
    
    print("\nExample usage:")
    print("""
    from pdf_extractor import PDFExtractor, extract_invoice_fields
    
    # Extract everything
    extractor = PDFExtractor()
    result = extractor.extract("invoice.pdf")
    
    # Access data
    print(f"Pages: {result.page_count}")
    print(f"Tables found: {len(result.tables)}")
    
    # Export
    extractor.to_csv(result, "table.csv")
    extractor.to_json(result, "full_data.json")
    
    # Smart field extraction
    fields = extract_invoice_fields(result)
    print(f"Invoice #: {fields.get('invoice_number')}")
    print(f"Total: {fields.get('total')}")
    """)


if __name__ == "__main__":
    demo()
