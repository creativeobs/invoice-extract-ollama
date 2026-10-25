from supabase import create_client, Client
import os
from dotenv import load_dotenv

# Manage metadata, extraction results, and log tables in Supabase
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

    def insert_extraction_result(self, result):
        try:
            response = self.__supabase.table("invoice Extraction Data").insert(result).execute()
        except:
            raise ValueError("Failed to insert data into Supabase. Please check your connection and table schema.")

    def log_execution(self, type:str, message:str):
        try:
            log_entry = {
                "type": type,
                "message": message
            }
            response = self.__supabase.table("invoice Extraction Logs").insert(log_entry).execute()
        except:
            raise ValueError("Failed to log execution in Supabase. Please check your connection and table schema.")