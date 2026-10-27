from langchain_ollama import ChatOllama
from dotenv import load_dotenv
from invoice_extraction.InvoiceSchema import invoiceData
from invoice_extraction.InvoiceSupabase import SupabaseManager
from invoice_extraction.InvoiceSupplier import InvoiceSupplier
from invoice_extraction.InvoiceOcr import InvoiceOcr
import json
import os


class InvoiceExtractor:

    load_dotenv()

    def __init__(self, to_db: bool = True):

        self.__fields = ["invoice_number", "invoice_date", "total_amount", "supplier", "currency"]

        try:
            self.__supabase = SupabaseManager() if to_db else None
            self.__ocr = InvoiceOcr(self.__supabase)

            self.__field_extractor = os.getenv("FIELD_EXTRACT") or "gemma4:31b-cloud"
            self.__llm = ChatOllama(
                model= self.__field_extractor,
                base_url="http://localhost:11434",
                temperature=0.1,
            )
            print("LLM Model initialized!")
            if self.__supabase: self.__supabase.log_execution("INFO", f"LLM Model initialized with {self.__field_extractor}")

            self.__sys_message = f"""
                You are an invoice information extraction engine. Extract ONLY these fields:

                {self.__fields}

                For EVERY field, return an object containing:
                - value: the extracted value or null
                - confidence_level: a number between 0.0 and 1.0
                - reason: a brief explanation based on the document evidence
                
                RULES:
                    1. If a field is missing, return null.
                    2. Return any date variables into this format: "MM/DD/YYYY"
                    3. Return any amount variables into this format: "0.00"
                    4. Never invent or calculate missing invoice information.
                    5. Do not extract additional fields.
                    6. Follow the provided structured output schema.
            """

        except Exception:
            if self.__supabase: self.__supabase.log_execution("ERROR", "Failed to initialize OCR or LLM model. Please check your configuration.")
            raise

    def __parse_results(self, res: json) -> dict:
        new_load = {}
        for x in res:
            for y in res[x]:
                key = x + '_' + y
                new_load[key] = res[x][y]
        return new_load
    
    def extract_invoice(self, path: str) -> dict:
        try:
            if self.__supabase: self.__supabase.log_execution("INFO", f"Starting invoice extraction for {path}")

            self.__ocr_result = self.__ocr.get_ocr_results(path)
            self.__user_message = f"""
            Extract the invoice data from the following document.

            <Document>
            {self.__ocr_result}
            </Document>
            """

            self.__message = [
                ('system', self.__sys_message),
                ('human', self.__user_message)
            ]
            
            self.__field_result = self.__parse_results(self.__llm.with_structured_output(invoiceData).invoke(self.__message).model_dump(mode='json'))
            if self.__supabase: self.__supabase.log_execution("INFO", f"Extraction completed for {path}")


            self.__supplierMatch = InvoiceSupplier(self.__llm)
            self.__supplierLookup = self.__supplierMatch.supplier_match(self.__field_result.get("supplier_value"))
            self.__to_db =  self.__field_result | self.__supplierLookup
            
            if self.__supabase:
                self.__supabase.insert_extraction_result(self.__to_db)
                print('Stored to DB') 
                self.__supabase.log_execution("INFO", f"Extraction result stored to DB for {path}")

        except Exception:
            if self.__supabase: self.__supabase.log_execution("ERROR", "Failed to extract invoice data. Please check your input and model configuration.")
            raise

        return self.__to_db