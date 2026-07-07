# TCE Universal Bid Comparison Engine

## Goal

Universal template-driven bid comparison engine.

Supports:

- Structured PDFs
- Semi-Structured PDFs
- Unstructured PDFs

Processes 6-10 PDFs simultaneously.

Generates bid comparison Excel workbook.

Never vendor-specific.

---

## PDF Pipeline

### Structured

PDF
→ Table Extraction
→ Rule Matching
→ Validation

### Semi-Structured

PDF
→ Keywords
→ Rules
→ Regex Fallback
→ Validation

### Unstructured

PDF
→ Hybrid Search
→ Semantic Retrieval
→ LLM Extraction

---

## Hybrid Retrieval

Combine:

- MiniLM Embeddings
- BM25 Search
- Semantic Search

Formula:

FinalScore =
0.6 × SemanticSimilarity
+
0.4 × BM25

---

## Embeddings

Model:

all-MiniLM-L6-v2

Store in FAISS.

Use ANN retrieval.

---

## Chunking

Use section-based chunking.

Examples:

Commercial Terms
Technical Scope
Price Schedule
Delivery
Warranty
Taxes
Payment Terms

Do NOT token chunk.

---

## LLM

Primary:

Qwen3:8B

Fallback:

Mistral:7B

Run through Ollama.

---

## Extraction

Extract one field at a time.

Return:

{
"value":"",
"confidence":0,
"evidence":""
}

---

## Confidence

Based on:

- Method used
- Evidence strength
- Similarity score
- Validation score

Realistic confidence only.

---

## Dynamic Template

Excel template controls extraction.

Workflow:

Read Template
→ Discover Fields
→ Build Extraction Plan
→ Extract
→ Populate Workbook

No code changes required if columns change.

---

## Excel Sheets

1. Bid Comparison
2. Vendor Ranking
3. Engine Profiles
4. Engine Evidence
5. Engine Fill Log
6. Confidence Report

---

## Excel Colors

Green = Rule

Blue = Regex

Yellow = Semantic

Orange = LLM

Red = Confidence < 75

---

## AI Assistant

Chat with processed PDFs.

Questions:

- Lowest cost vendor
- Delivery comparison
- Warranty comparison
- Payment terms comparison
- Evidence lookup
- Confidence explanation
- Vendor ranking rationale

Answer only from extracted evidence.

No hallucinations.

---

## Vendor Scoring

Inputs:

- Price
- Delivery
- Warranty
- Compliance
- Taxes
- Payment Terms

Output:

Vendor Ranking

Explain score breakdown.

---

## Frontend

Bootstrap 5

TCE Branding

White Theme

TCE Logo top-left

Features:

- Multi PDF Upload
- Template Upload
- Progress Monitor
- Vendor Dashboard
- AI Assistant Chat
- Download Results

---

## Progress Tracking

Show per-PDF:

- Extraction
- Embeddings
- Retrieval
- LLM
- Excel Fill

---

## Storage

storage/

uploads/
vectors/
outputs/
logs/
evidence/
engine_profiles/
excel_reports/
templates/

---

## Backend

Python 3.12

Flask

FAISS

SentenceTransformers

Rank-BM25

PDFPlumber

PyMuPDF

OpenPyXL

Ollama

Pydantic

RapidFuzz

---

## Requirement

Generate complete project incrementally.

Maintain:

- folder structure
- completed files
- pending files

If context limit reached:

Output all generated files before stopping.
i have tried doing 35%
note:make changes if necessary or not working properly.
workflow recommended 
GitHub Repo
│
├── README.md
├── PROJECT_SPEC.md
├── PROJECT_STATE.md
├── app.py
├── backend/
├── core/
├── extractors/
├── llm/
├── pdf/
├── excel/
├── storage/
└── templates/