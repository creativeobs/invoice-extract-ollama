from langchain_ollama import ChatOllama
from InvoiceSchema import SupplierMatch
from InvoiceSupabase import SupabaseManager

class InvoiceSupplier:
    def __init__(self, 
                 model: ChatOllama = None,
                 supabase: SupabaseManager = None):
        try:
            if model is None or supabase is None:
                raise ValueError("Model and SupabaseManager instances must be provided.")

            self.__llm = model.with_structured_output(SupplierMatch)
            self.__supabase = supabase

            self.__suppliers = self.__supabase.get_supplier_table()
            
            self.__sys_message = f"""
                You are a supplier matcher agent.
                You will review and recommend the most appropriate supplier lookup in the database.
                Rules:
                    1. Create a valid JSON output
                    2. the JSON should contain supplier_lookup_value, supplier_lookup_confidence_level, and supplier_lookup_reason.
                    3. Confidence level should be between 0.0 and 1.0
                    4. If confidence level is < 0.7, do not recommend anything at all and just return supplier_lookup_value = None, supplier_lookup_confidence_level = 0.0, and supplier_lookup_reason = "No confident match found."
                    5. If confidence level is >= 0.7, return the most appropriate supplier
                    6. The supplier loookup database contains 2 fields (supplier and alternate_name). Return only supplier as the value and use both fields as your reference.

                <supplier lookup database>
                {self.__suppliers}
                </supplier lookup database>
            """
        except:
            self.__supabase.log_execution("ERROR", f"Failed to initialize LLM Model")
            raise

    def supplier_match(self, supplier: str) -> dict:
        try:
            self.__user_message = f"""
                Retrieve the appropriate supplier for this raw supplier name: "{supplier}"
            """
            return self.__llm.invoke([('system', self.__sys_message),
                                      ('human', self.__user_message)]).model_dump(mode='json')
        except:
            self.__supabase.log_execution('Error', 'Supplier Matching Failed!')
            raise