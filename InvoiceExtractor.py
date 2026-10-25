from paddleocr import PaddleOCR
from langchain_ollama import ChatOllama
from dotenv import load_dotenv
from InvoiceSchema import invoiceData
from InvoicetoSupabase import SupabaseManager
import json
import os

class InvoiceExtractor:

    load_dotenv()

    def __init__(self, 
                 text_recog: str = os.getenv("TEXT_RECOG") or "PP-OCRv5_mobile_rec", 
                 text_detect: str = os.getenv("TEXT_DETECT") or "PP-OCRv5_mobile_det",
                 field_extractor: str = os.getenv("FIELD_EXTRACT") or "gemma4:31b-cloud"):

        self.__fields = ["invoice_number", "invoice_date", "total_amount", "supplier", "currency"]
        self.__supabase = SupabaseManager()

        try:
            self.__ocr = PaddleOCR(
                text_detection_model_name = text_detect,
                text_recognition_model_name = text_recog,
                use_doc_orientation_classify=False,
                use_doc_unwarping=False,
                use_textline_orientation=False,
            )
            print(f"OCR Model initialized!")
            self.__supabase.log_execution("INFO", f"OCR Model initialized with {text_recog} and {text_detect}")

            self.__llm = ChatOllama(
                model=field_extractor,
                base_url="http://localhost:11434",
                temperature=0.1,
            ).with_structured_output(invoiceData)

            print("LLM Model initialized!")
            self.__supabase.log_execution("INFO", f"LLM Model initialized with {field_extractor}")

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
            self.__supabase.log_execution("ERROR", "Failed to initialize OCR or LLM model. Please check your configuration.")
            raise

    @property
    def ocr(self):
        return self.__ocr

    @ocr.setter
    def ocr(self, text_recog: str, text_detect: str):
        try:
            self.__ocr = PaddleOCR(
                text_detection_model_name = text_detect,
                text_recognition_model_name = text_recog,
                use_doc_orientation_classify=False,
                use_doc_unwarping=False,
                use_textline_orientation=False,
            )
        except Exception:
            self.__supabase.log_execution("ERROR", "Failed to update OCR model. Please check your configuration.")
            raise

        print('OCR Model updated!')
        self.__supabase.log_execution("INFO", f"OCR Model updated with {text_recog} and {text_detect}")

    @property
    def llm(self):
        return self.__llm

    @llm.setter
    def llm(self, field_extractor:str):
        try:
            self.__llm = ChatOllama(
                model=field_extractor,
                base_url="http://localhost:11434",
                temperature=0.1,
            ).with_structured_output(invoiceData)
        except Exception:
            self.__supabase.log_execution("ERROR", "Failed to initialize LLM model. Please check your configuration.")
            raise

        print('Model updated!')

    def __parse_results(self, res: json) -> dict:
        new_load = {}
        for x in res:
            for y in res[x]:
                key = x + '_' + y
                new_load[key] = res[x][y]
        return new_load
    
    def extract_invoice(self, path: str, store_to_db: bool = False):
        try:
            self.__supabase.log_execution("INFO", f"Starting invoice extraction for {path}")
            self.__ocr_result = self.__ocr.predict(path)
            self.__user_message = f"""
            Extract the invoice data from the following document.

            <Document>
            {self.__ocr_result}
            </Document>
            """

            self.message = [
                ('system', self.__sys_message),
                ('human', self.__user_message)
            ]
            
            self.__field_result = self.__parse_results(self.__llm.invoke(self.message).model_dump(mode='json'))

            if store_to_db:
                self.__supabase.insert_extraction_result(self.__field_result)
                print('Stored to DB') 
                self.__supabase.log_execution("INFO", f"Extraction result stored to DB for {path}")

        except Exception:
            self.__supabase.log_execution("ERROR", "Failed to extract invoice data. Please check your input and model configuration.")
            raise

        return self.__field_result