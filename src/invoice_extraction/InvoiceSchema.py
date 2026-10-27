from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from decimal import Decimal

class fieldValues[T] (BaseModel):
    value: T | None = Field(description="Extracted value, or null if missing")
    confidence_level: float | None = Field(description="Expected Confidence Level", ge=0.0, le=1.0)
    reason: str | None = Field(description="Brief explanation of your extracted value.")

class dateValues(BaseModel):
    value: str | None = Field(description="Extracted value, or null if missing")
    confidence_level: float | None = Field(description="Expected Confidence Level", ge=0.0, le=1.0)
    reason: str | None = Field(description="Brief explanation of your extracted value.")

    @field_validator("value", mode='before')
    @classmethod
    def normalize_date_values(cls, value):
        if value == None: return value
        if isinstance(value, str):
            value = value.strip()
            if value == datetime.strptime(value, "%m/%d/%Y").strftime("%m/%d/%Y"):
                return value
        raise ValueError('Unsupported date format')

class SupplierMatch(BaseModel):
    supplier_lookup_value: str | None = Field(description="Closest Supplier Match or null if missing")
    supplier_lookup_confidence_level: float | None = Field(description="Expected Confidence Level", ge=0.0, le=1.0)
    supplier_lookup_reason: str | None = Field(description="Brief explanation of your extracted value.")

class invoiceData(BaseModel):
    invoice_number: fieldValues[str] 
    invoice_date: dateValues 
    total_amount: fieldValues[Decimal] 
    supplier: fieldValues[str]
    currency: fieldValues[str]

