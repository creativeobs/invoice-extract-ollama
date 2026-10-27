from supabase import create_client
import os
from dotenv import load_dotenv
from retry import retry

class SupabaseManager:
    def __init__(self):
        load_dotenv()
        try:
            self.__supabase_url = os.getenv("SUPABASE_URL") 
            self.__supabase_key = os.getenv("SUPABASE_KEY")
            self.__supabase = create_client(self.__supabase_url, self.__supabase_key)
        except:
            raise ValueError("Supabase URL or Key not found in environment variables.")

    @retry(tries=3, delay=1, backoff=2)
    def insert_extraction_result(self, result) -> None:
        try:
            self.__supabase.table("invoice Extraction Data").insert(result).execute()
        except:
            self.log_execution("ERROR", f"Failed to insert data into Supabase: {result}")
            raise
        
    @retry(tries=3, delay=1, backoff=2)
    def get_supplier_table(self) -> dict:
        try:
            response = self.__supabase.table("supplier_tbl").select("*").execute()
        except:
            self.log_execution("ERROR", "Failed to retrieve supplier table from Supabase.")
            raise 
        return response.data or []

    @retry(tries=3, delay=1, backoff=2)
    def log_execution(self, type:str, message:str):
        try:
            log_entry = {
                "type": type,
                "message": message
            }
            self.__supabase.table("invoice Extraction Logs").insert(log_entry).execute()
        except:
            raise ValueError("Failed to log execution in Supabase. Please check your connection and table schema.")