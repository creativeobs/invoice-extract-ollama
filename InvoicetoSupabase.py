from supabase import create_client, Client
import os
from dotenv import load_dotenv
from retry import retry

class SupabaseManager:
    def __init__(self):
        load_dotenv()
        try:
            self.__supabase_url = os.getenv("SUPABASE_URL") 
            self.__supabase_key = os.getenv("SUPABASE_KEY")
            self.__supabase: Client = create_client(self.__supabase_url, self.__supabase_key)
            print("Supabase client initialized!")
        except:
            raise ValueError("Supabase URL or Key not found in environment variables.")

    @retry(tries=3, delay=1, backoff=2)
    def insert_extraction_result(self, result):
        try:
            response = self.__supabase.table("invoice Extraction Data").insert(result).execute()
        except:
            raise ValueError("Failed to insert data into Supabase. Please check your connection and table schema.")

    @retry(tries=3, delay=1, backoff=2)
    def log_execution(self, type:str, message:str):
        try:
            log_entry = {
                "type": type,
                "message": message
            }
            response = self.__supabase.table("invoice Extraction Logs").insert(log_entry).execute()
        except:
            raise ValueError("Failed to log execution in Supabase. Please check your connection and table schema.")