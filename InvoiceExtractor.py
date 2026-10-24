from paddleocr import PaddleOCR
from langchain_ollama import ChatOllama
from dotenv import load_dotenv
from InvoiceSchema import invoiceData
import os

class InvoiceExtractor:

    load_dotenv()

    def __init__(self, 
                 text_recog: str = os.getenv("TEXT_RECOG") or "PP-OCRv5_mobile_rec", 
                 text_detect: str = os.getenv("TEXT_DETECT") or "PP-OCRv5_mobile_det",
                 field_extractor: str = os.getenv("FIELD_EXTRACT") or "gemma4:31b-cloud",
                 fields: list[str] = ["invoice_number", "invoice_date", "total_amount"]):

        try:
            self.__ocr = PaddleOCR(
                text_detection_model_name = text_detect,
                text_recognition_model_name = text_recog,
                use_doc_orientation_classify=False,
                use_doc_unwarping=False,
                use_textline_orientation=False,
            )
            print(f"OCR Model initialized!")

            self.__llm = ChatOllama(
                model=field_extractor,
                base_url="http://localhost:11434",
                temperature=0.1,
            ).with_structured_output(invoiceData)

            print("LLM Model initialized!")

            self.__sys_message = f"""
                You are an invoice information extraction engine. Extract ONLY these fields:

                {fields}

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
            raise

        print('OCR Model updated!')

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
            )
        except Exception:
            raise

        print('Model updated!')

    def extract_invoice(self, path: str):
        try:
            self.__ocr_result = self.__ocr.predict(path)
            self.__user_message = f"""
            Extract the invoice data from the following document.

            <Document>
            {self.__ocr_result}
            </Document>
            """

            self.message = [
                ('user', self.__sys_message),
                ('human', self.__user_message)
            ]
            
            field_result = self.__llm.invoke(self.message)

        except Exception:
            raise

        return field_result