# AI-Powered Invoice Extraction

An AI-powered invoice extraction pipeline that transforms unstructured invoice documents into structured, validated data using Optical Character Recognition (OCR), Large Language Models (LLMs), and Pydantic.

The project combines OCR-based text extraction with LLM-powered information extraction and schema validation to convert invoice data into a consistent format for downstream processing.

## Overview

Invoices often contain inconsistent layouts, date formats, currency symbols, and financial information. Extracting these fields manually can be time-consuming and error-prone.

This project explores an automated approach to invoice processing by combining document text extraction, structured LLM output, and Python-based data validation.

### Key Features

- **OCR processing:** Extract text from invoice documents using PaddleOCR.
- **LLM-powered extraction:** Use LangChain and Ollama to extract relevant invoice information from OCR text.
- **Structured output:** Define the expected response format using Pydantic models.
- **Schema validation:** Validate extracted field types and reject unexpected fields.
- **Data normalization:** Handle common date formats and currency-formatted amounts.
- **Missing-value handling:** Represent missing or unreadable values as `null` rather than inventing information.
- **Extensible architecture:** Separate extraction, validation, and downstream processing responsibilities.

## Architecture

The pipeline follows a modular extraction workflow:

```text
Invoice Document
       |
       v
OCR Processing
   (PaddleOCR)
       |
       v
Extracted OCR Text
       |
       v
LLM Information Extraction
 (LangChain + Ollama)
       |
       v
Structured Output
   (InvoiceData)
       |
       v
Pydantic Validation
 and Normalization
       |
       v
Validated Invoice Data
       |
       v
Downstream Processing
```

Each component serves a distinct purpose:

| Component | Responsibility |
|---|---|
| PaddleOCR | Extract text from invoice documents |
| LangChain | Orchestrate model calls and structured output |
| Ollama | Provide access to a locally hosted LLM |
| Pydantic | Validate data types, field definitions, and constraints |
| Python validators | Normalize supported date and monetary formats |

## Extracted Fields

The current invoice schema focuses on three fields.

| Field | Data type | Description |
|---|---|---|
| `invoice_number` | `str \| None` | Invoice identifier |
| `invoice_date` | `date \| None` | Invoice issue date |
| `total_amount` | `Decimal \| None` | Final amount due or total payable |

The extraction rules prioritize the final amount due rather than the subtotal, individual taxes, or line-item amounts.

If a field is missing or cannot be determined from the document, the pipeline should return `null` instead of fabricating a value.

## Technology Stack

- **Python 3.12+** — Core development language
- **uv** — Python project and dependency management
- **PaddleOCR** — Optical character recognition
- **LangChain** — LLM orchestration and structured output
- **Ollama** — Local LLM runtime
- **Pydantic v2** — Schema definition and validation
- **Pandas** — Data manipulation and tabular processing

## Getting Started

### Prerequisites

Install the following before running the project:

- Python 3.12 or later
- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- [Ollama](https://ollama.com/download)
- A compatible Ollama model

PaddleOCR may also require additional system libraries or model downloads depending on your operating system and OCR configuration.

### 1. Clone the repository

```bash
git clone --branch dev https://github.com/creativeobs/invoiceExtraction.git
cd invoiceExtraction
```

### 2. Install dependencies

```bash
uv sync
```

This installs the dependencies declared in `pyproject.toml` and creates or updates the project's virtual environment.

### 3. Configure Ollama

Start the Ollama service and download a model compatible with your implementation.

For example:

```bash
ollama pull qwen2.5:7b
```

Start the service if it is not already running:

```bash
ollama serve
```

Ollama's local API typically runs at `http://localhost:11434`.

**Note:** The model name above is an example. Use the model configured in your application and ensure it supports the structured-output features required by your LangChain integration.

### 4. Run the project

Activate the environment if needed:

```bash
uv run python -c "import invoice_extraction; print('Package imported successfully')"
```

The project also declares an `invoice-extraction` command-line entry point. Once its `main` function is implemented and configured, you can invoke it with:

```bash
uv run invoice-extraction
```

For notebook-based development, start Jupyter using the project environment:

```bash
uv run jupyter notebook
```

## Structured Output and Validation

The extraction schema defines the expected fields and their types. LangChain passes the schema to the LLM integration, while Pydantic validates the resulting data.

A simplified example:

```python
from datetime import date
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field


class InvoiceData(BaseModel):
    model_config = ConfigDict(extra="forbid")

    invoice_number: str | None = None
    invoice_date: date | None = None
    total_amount: Decimal | None = Field(
        default=None,
        ge=0,
    )
```

The model should be configured to return only the defined fields. Additional Python validators can normalize supported date and amount formats before validation.

For example, the following OCR values:

```text
Invoice Number: INV-001
Invoice Date: 13-07-2023
Total Due: $2,510.00
```

Can be normalized into:

```json
{
  "invoice_number": "INV-001",
  "invoice_date": "2023-07-13",
  "total_amount": "2510.00"
}
```

The JSON example represents the serialized data; the Pydantic model uses Python `date` and `Decimal` objects internally.

### Validation Principles

1. Reject unexpected fields.
2. Normalize supported date and monetary formats.
3. Preserve missing values as `None`.
4. Avoid inventing missing invoice information.
5. Distinguish schema validity from factual extraction accuracy.
6. Route invalid or ambiguous results for further processing or human review.

Pydantic validates data against the defined rules, but schema validity alone does not guarantee that the extracted values accurately reflect the original document.

## Project Configuration

Project dependencies and build configuration are defined in `pyproject.toml`.

To inspect the installed dependencies:

```bash
uv pip list
```

To add a new dependency:

```bash
uv add package-name
```

For development-only dependencies:

```bash
uv add --dev package-name
```

## Development Roadmap

Potential next steps for the project include:

- [ ] Expand extraction to additional invoice fields.
- [ ] Add automated unit tests for schemas and normalization.
- [ ] Implement retry and error-handling strategies for failed model responses.
- [ ] Add extraction-quality evaluations against labeled invoice samples.
- [ ] Validate extracted amounts against invoice totals and tax breakdowns.
- [ ] Add confidence-based review for ambiguous or incomplete extractions.
- [ ] Export validated results to CSV, Excel, or a downstream business system.
- [ ] Add structured logging and monitoring for production workflows.

## Contributing

Contributions and suggestions are welcome. When extending the pipeline, keep extraction prompts, schema definitions, normalization rules, and business validations clearly separated.

## License

No license has been specified in this README. Add the appropriate license information once the repository's licensing terms have been established.
