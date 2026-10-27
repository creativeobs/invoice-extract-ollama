
from invoice_extraction.InvoiceExtractor import InvoiceExtractor

TESTS_DIR = "./tests"

expected_results = {
    "invoice_001_usd.pdf": {
        "invoice_number": "NS-2026-1048",
        "invoice_date": "03/14/2026",
        "total_amount": 1342.30,
        "supplier": "Northstar Office Supplies LLC",
        "currency": "USD",
        "supplier_lookup" : "Northstar Office",
    },
    "invoice_002_eur.pdf": {
        "invoice_number": "BDS-26-7781",
        "invoice_date": "07/22/2026",
        "total_amount": 3332.00,
        "supplier": "Berlin Data Systems GmbH",
        "currency": "EUR",
        "supplier_lookup": "Berlin Data Systems GmbH",
    },
    "invoice_003_gbp.pdf": {
        "invoice_number": "HF-INV-00931",
        "invoice_date": "01/09/2026",
        "total_amount": 1170.60,
        "supplier": "Harbor & Finch Consulting Ltd",
        "currency": "GBP",
        "supplier_lookup": "Harbor & Finch Consulting Ltd",
    },
    "invoice_004_php.pdf": {
        "invoice_number": "MCS-2026-0412",
        "invoice_date": "10/05/2026",
        "total_amount": 54320.00,
        "supplier": "Manila Creative Studio Inc.",
        "currency": "PHP",
        "supplier_lookup": "Manila Creative Studio Inc.",
    },
    "invoice_005_usd.pdf": {
        "invoice_number": "CPCS-INV-56002",
        "invoice_date": "12/18/2025",
        "total_amount": 699.00,
        "supplier": "Cedar Peak Cloud Services",
        "currency": "USD",
        "supplier_lookup": "Cedar Peak Cloud Services",
    },
}

def test_invoice_accuracy():
    extractor = InvoiceExtractor()
    errors = []

    for filename, expected in expected_results.items():
        pdf_path = 'tests/' + filename
        actual = extractor.extract_invoice(str(pdf_path), store_to_db=False)

        for field, expected_value in expected.items():
            actual_value = actual.get(f"{field}_value")

            if actual_value != expected_value:
                errors.append(
                    f"{filename}: {field} "
                    f"(expected {expected_value!r}, got {actual_value!r})"
                )

    assert not errors, "\n".join(errors)