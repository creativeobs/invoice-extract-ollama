from invoice_extraction.InvoiceExtractor import InvoiceExtractor

def main() -> int:
    ie = InvoiceExtractor(to_db=True)
    src = input("Enter the path to the invoice file (PDF, PNG, or JPEG): ")
    res = ie.extract_invoice(src)
    print(res)

if __name__ == "__main__":
    main()