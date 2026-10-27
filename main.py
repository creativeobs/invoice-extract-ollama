from InvoiceExtractor import InvoiceExtractor

if __name__ == "__main__":
    ie = InvoiceExtractor()
    src = input("Enter the path to the invoice file (PDF, PNG, or JPEG): ")
    res = ie.extract_invoice(src, store_to_db=True)
    print(res)