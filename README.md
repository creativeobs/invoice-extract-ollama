# AI-Powered Invoice Extraction

An AI-assisted invoice processing pipeline that converts PDF and image-based invoices into structured data using PaddleOCR, LangChain, Ollama, and Pydantic. The workflow extracts invoice fields, attaches field-level confidence estimates and explanations, matches suppliers against reference records, and supports persistence to Supabase.

> **Project status:** Portfolio / development project. Extraction, validation, supplier matching, and database integration are implemented, but the current test interface and database coupling need further work before the pipeline can be considered reliable for production use.

## Overview

Invoice data is often embedded in documents with inconsistent layouts, date formats, currency symbols, and supplier names. This project explores how OCR and large language models can automate field extraction while retaining structured validation and traceable explanations.

### Features

- **Document OCR:** Uses PaddleOCR to recognize text from invoice documents.
- **LLM-based extraction:** Uses LangChain and Ollama to extract structured invoice information.
- **Schema validation:** Uses Pydantic models to define expected fields and validate model output.
- **Field-level explanations:** Captures a confidence estimate and a reason for each extracted field.
- **Supplier matching:** Uses an LLM to recommend a matching supplier from Supabase supplier records.
- **Database integration:** Supports storing extraction results and execution logs in Supabase.
- **Retry handling:** Uses retry decorators for selected Supabase operations.
- **Accuracy evaluation:** Includes a labeled set of five sample invoices for field-level comparison.

## Architecture

```text
Invoice PDF / Image
        |
        v
PaddleOCR
        |
        v
Recognized Invoice Text
        |
        v
LangChain + Ollama
        |
        v
Pydantic Structured Output
        |
        v
Field Parsing and Validation
        |
        v
Supplier Matching
        |
        v
Structured Extraction Result
        |
        v
Supabase Persistence
```

### Technology stack

| Technology | Responsibility |
|---|---|
| Python 3.12+ | Application logic |
| uv | Dependency and environment management |
| PaddleOCR | Optical character recognition |
| LangChain | LLM orchestration and structured output |
| Ollama | Model runtime and model access |
| Pydantic | Data schemas and validation |
| Supabase | Supplier reference data, extraction results, and logs |
| pytest | Automated testing |

## Extracted fields

The current invoice schema defines five business fields. Each field includes a value, a confidence estimate, and a reason.

| Field | Intended value |
|---|---|
| `invoice_number` | Invoice identifier |
| `invoice_date` | Invoice date in `MM/DD/YYYY` format |
| `total_amount` | Invoice total represented using `Decimal` |
| `supplier` | Supplier name extracted from the document |
| `currency` | Currency code or value identified from the invoice |

Supplier matching adds these fields:

- `supplier_lookup_value`
- `supplier_lookup_confidence_level`
- `supplier_lookup_reason`

The extraction prompt instructs the model to return missing fields as `null` rather than inventing information. Confidence values are model-generated estimates and should not be treated as calibrated probabilities.

## Project structure

```text
invoice-extract-ollama/
├── src/
│   └── invoice_extraction/
│       ├── __init__.py
│       ├── cli.py
│       ├── InvoiceExtractor.py
│       ├── InvoiceOcr.py
│       ├── InvoiceSchema.py
│       ├── InvoiceSupplier.py
│       └── InvoiceSupabase.py
├── tests/
│   └── test_invoice_accuracy.py
├── notebook/
├── .env.example
├── .gitignore
├── pyproject.toml
├── requirements.txt
├── uv.lock
└── README.md
```

- `cli.py` — command-line entry point.
- `InvoiceExtractor.py` — coordinates extraction, structured output, and supplier matching.
- `InvoiceOcr.py` — initializes PaddleOCR and converts recognized text into a string.
- `InvoiceSchema.py` — defines extraction and supplier-match schemas.
- `InvoiceSupplier.py` — matches the extracted supplier against reference records.
- `InvoiceSupabase.py` — manages database access, persistence, and execution logs.
- `tests/test_invoice_accuracy.py` — compares extraction output against expected values for sample invoices.

## Getting started

### Prerequisites

Install the following:

- Python 3.12 or later
- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- [Ollama](https://ollama.com/download)
- A compatible Ollama model
- A Supabase project with the required tables for the current integrated workflow

PaddleOCR may download model assets during initialization and may require additional operating-system dependencies.

### 1. Clone the repository

```bash
git clone https://github.com/creativeobs/invoice-extract-ollama.git
cd invoice-extract-ollama
```

### 2. Install dependencies

```bash
uv sync
```

This installs the dependencies declared in `pyproject.toml` and creates or updates the local virtual environment.

The `.venv/` directory is intentionally excluded from version control. Each developer should create their own environment using `uv sync`.

### 3. Configure environment variables

Create a local `.env` file from the template:

```bash
cp .env.example .env
```

Configure the following values:

```dotenv
SUPABASE_URL=
SUPABASE_KEY=

TEXT_RECOG=PP-OCRv5_mobile_rec
TEXT_DETECT=PP-OCRv5_mobile_det
FIELD_EXTRACT=gemma4:31b-cloud
```

Use the model name appropriate for your Ollama setup. The model configured in the application must be available to that runtime and support the structured-output behavior required by the integration.

**Security:** Never commit `.env` or expose Supabase credentials in source code, notebooks, logs, or screenshots. If a real key has been exposed, rotate it.

### 4. Configure Ollama

Start Ollama if it is not already running:

```bash
ollama serve
```

The application currently uses the Ollama API at:

```text
http://localhost:11434
```

Ensure the configured model is available before running the extraction workflow. Model availability and hardware requirements depend on the selected model.

### 5. Run the CLI

The package defines the `invoice-extraction` command:

```bash
uv run invoice-extraction
```

The current CLI prompts for an invoice file path, runs extraction, and prints the resulting data.

**Current behavior:** the CLI initializes `InvoiceExtractor(to_db=True)`, so it enables database persistence. Configure Supabase before running the CLI. An explicit `--save` option and a database-independent extraction mode are recommended future improvements.

Supported document types are intended to include PDF, PNG, JPG, and JPEG files.

## Supabase integration

The current implementation references these tables:

| Table | Purpose |
|---|---|
| `supplier_tbl` | Supplier names and alternate names used for matching |
| `invoice Extraction Data` | Stores extraction results |
| `invoice Extraction Logs` | Stores execution and error logs |

These names must match the tables configured in your Supabase project. The current implementation uses the Supabase Python client to retrieve supplier records, insert extraction results, and write execution logs.

<img width="1856" height="424" alt="image" src="https://github.com/user-attachments/assets/72791590-ae0e-4485-a905-58131f4495fe" />
![Uploading image.png…]()


Avoid logging complete invoice contents or sensitive financial information. Prefer recording execution IDs, processing stages, durations, and sanitized error messages.

## Evaluation and testing

The repository includes five labeled sample invoices covering USD, EUR, GBP, and PHP examples. The expected outputs include invoice identifiers, dates, amounts, supplier names, currencies, and supplier lookup values.

Run the current accuracy test with:

```bash
uv run pytest tests/test_invoice_accuracy.py -v
```

## Engineering goals

This project is intended to demonstrate applied AI engineering through the integration of document processing, structured LLM output, schema validation, business-record matching, database persistence, and automated evaluation.

The long-term objective is to evolve the prototype into a more reliable document-processing workflow with testable components, measurable extraction quality, clear failure handling, and human review for uncertain results.
