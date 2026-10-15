# Marksheet AI Enterprise — Academic Document Intelligence & Analytics

A production-ready SaaS suite for academic marksheet extraction, verification, analytics, and reporting. Converts printed, scanned, and digital marksheets into structured data with multi-engine OCR, validation rules, live editable results, and full export capabilities (Excel, PDF, CSV, JSON).

---

## 🌟 Key Features

### 1. Multi-Engine Extraction Architecture
- **⚡ Local OCR / Document Engine**:
  - 100% private and offline — runs entirely on your local machine.
  - Native digital PDF parsing and multi-student broadsheet extraction.
  - Requires **zero API keys** or external network requests.
- **🤖 Groq Vision AI (Multimodal LLM)**:
  - Powered by `llama-3.2-11b-vision-preview` and `llama-3.2-90b-vision-preview`.
  - Automatic PDF-to-image rendering with high-DPI scaling.
  - Contrast enhancement and pre-processing for faint scans.
- **🌐 FastAPI Backend Microservice**:
  - Supports decoupled horizontal scaling and batch processing.

### 2. Enterprise UI/UX Dashboard
- Dark navy SaaS interface with glassmorphic cards and Inter typography.
- Real-time KPI cards: Total Documents, Verified Extractions, Review Needed, Average Latency, and Candidates Evaluated.
- Dynamic charts showing extraction volume by date and academic classification distribution.

### 3. Advanced Document Ingestion
- Drag-and-drop batch upload for PDF, PNG, JPG, JPEG documents up to 25 MB.
- File integrity checking, MIME validation, and SHA-256 duplicate detection.
- Fast multi-page preview powered by `pypdfium2`.

### 4. Interactive Results & Validation
- Candidate profile cards (Name, Roll No, Result, SGPA/GPA).
- Broadsheet cohort registry support with student switcher.
- **Interactive Editable Subject Table** with real-time recalculation of totals, percentages, pass/fail counts, and academic standings.
- **Validation Engine**: Detects component mismatches (`Internal + External != Total`), marks exceeding maximums, and missing identifiers.

### 5. Multi-Format Export Suite
- **Microsoft Excel (`.xlsx`)**: Styled multi-sheet workbooks with Openpyxl (Cohort Broadsheet + Subject Breakdown).
- **Printable PDF Summary (`.pdf`)**: Formal academic report generated with ReportLab.
- **Raw CSV (`.csv`)**: For database imports and spreadsheet analysis.
- **JSON Payload (`.json`)**: Formatted structured output with metadata and timestamps.

### 6. Local SQLite Persistence
- Automated local archiving in `marksheet_extractor.db`.
- Search, filter by engine or status, inspect past records, and single-click re-exports.

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- Python 3.10+
- Windows, macOS, or Linux

### 2. Installation
```powershell
# Clone or navigate to the repository
cd "student management"

# Activate virtual environment
.venv\Scripts\activate   # Windows
# or: source .venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

### 3. Running the Application
```powershell
streamlit run frontend/fapp.py --server.port 8501
```
Open **[http://localhost:8501](http://localhost:8501)** in your browser.

---

## ⚙️ Configuration (.env)

Copy `.env.example` to `.env` to configure optional credentials:
```ini
# Optional: Groq API Key for multimodal AI vision extraction on scanned images
# Get a free key at: https://console.groq.com/keys
GROQ_API_KEY=gsk_your_key_here

# Optional: Local backend URL
BACKEND_URL=http://localhost:8000
```

---

## 📁 Project Architecture

```
student management/
├── frontend/
│   ├── config.py           # Configuration, constants & credential security
│   ├── db.py               # SQLite database layer (marksheet_extractor.db)
│   ├── preprocessing.py    # File validation, SHA-256 hashing & PDF rendering
│   ├── validator.py        # Business logic validation & dynamic recalculation
│   ├── extractors.py       # Offline, Groq Vision, and Backend API engines
│   ├── exporters.py        # Excel (.xlsx), PDF (.pdf), CSV, and JSON generators
│   ├── ui_components.py    # SaaS design tokens, custom CSS & metric widgets
│   ├── fapp.py             # Main Streamlit SaaS application
│   └── requirements.txt    # Frontend dependencies
├── app/                    # FastAPI microservice backend
├── test_samples/           # Test marksheets & sample documents
├── .env.example            # Sample configuration file
├── requirements.txt        # Root dependency manifest
└── README.md               # System documentation
```

---

## 🔒 Security & Privacy

- All uploaded files and extracted academic records are stored strictly in your local SQLite database (`marksheet_extractor.db`).
- API keys are protected in `.env` and never logged or exposed in the client UI.
- Offline extraction mode operates completely offline without sending any document data to external servers.

---

## 👨‍💻 Author & Maintainer

Created and maintained by **duvvuruharshanthreddy** ([@Harshanthreddy](https://github.com/Harshanthreddy)).

© 2026 **Marksheet AI Enterprise**. All rights reserved by **duvvuruharshanthreddy**.

