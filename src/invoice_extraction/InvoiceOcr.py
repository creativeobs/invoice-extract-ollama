from paddleocr import PaddleOCR
from invoice_extraction.InvoiceSupabase import SupabaseManager
from dotenv import load_dotenv
import os

class InvoiceOcr:
    load_dotenv()
    def __init__(self, 
                 supabase: SupabaseManager = None, 
                 text_detect: str = os.getenv("TEXT_DETECT") or "PP-OCRv5_mobile_det",
                 text_recog: str = os.getenv("TEXT_RECOG") or "PP-OCRv5_mobile_rec"):
        try:
            self.__ocr = PaddleOCR(
                text_detection_model_name = text_detect,
                text_recognition_model_name = text_recog,
                use_doc_orientation_classify=False,
                use_doc_unwarping=False,
                use_textline_orientation=False,
            )
            self.__supabase = supabase

            if self.__supabase: self.__supabase.log_execution("INFO", f"OCR Model initialized with {text_recog} and {text_detect}")
            print("OCR Model Initialized!")

        except Exception:
            if supabase:
                self.__supabase.log_execution("ERROR", "Failed to initialize OCR model. Please check your configuration.")
            raise

    def get_ocr_results(self, path: str) -> str:
        try:
            self.ocr_results = ' '.join(self.__ocr.predict(path)[0]['rec_texts'])
            return self.ocr_results
        except Exception:
            if self.__supabase: self.__supabase.log_execution("ERROR", f"Failed to get OCR from {path}")
            raise