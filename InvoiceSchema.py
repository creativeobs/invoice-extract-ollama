from pydantic import BaseModel, Field, field_validator
from datetime import date

class fieldValues[T] (BaseModel):
    value: T | None = Field(description="Extracted value, or null if missing")
    confidence_level: float = Field(description="Expected Confidence Level", ge=0.0, le=1.0)
    reason: str = Field(description="Brief explanation of your extracted value.")

class invoiceData(BaseModel):
    invoice_number: fieldValues[str] = Field(description="Extract the invoice number or identifier")
    invoice_date: fieldValues[date] = Field(description="Extract the invoice date")
    total_amount: fieldValues[float] = Field(description="Extracted total_amount")