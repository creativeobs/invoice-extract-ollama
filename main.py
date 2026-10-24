from InvoiceExtractor import InvoiceExtractor

if __name__ == "__main__":
    ie = InvoiceExtractor()
    res = ie.extract_invoice("tests/invoice-1.png")
    ie._s
    print(res)