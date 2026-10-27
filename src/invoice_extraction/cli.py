from invoice_extraction.InvoiceExtractor import InvoiceExtractor
import pprint

def main() -> int:
    ie = InvoiceExtractor(to_db=False)
    src = input("Enter the path to the invoice file (PDF, PNG, or JPEG): ")
    res = ie.extract_invoice(src)
    pprint.pprint(res)

if __name__ == "__main__":
    main()