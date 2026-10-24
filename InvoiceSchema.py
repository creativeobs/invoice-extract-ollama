from pydantic import BaseModel, Field, field_validator
from datetime import date, datetime

class fieldValues[T] (BaseModel):
    value: T | None = Field(description="Extracted value, or null if missing")
    confidence_level: float = Field(description="Expected Confidence Level", ge=0.0, le=1.0)
    reason: str = Field(description="Brief explanation of your extracted value.")

class dateValues(BaseModel):
    value: date | None = Field(description="Extracted value, or null if missing")
    confidence_level: float = Field(description="Expected Confidence Level", ge=0.0, le=1.0)
    reason: str = Field(description="Brief explanation of your extracted value.")

    @field_validator("value", mode='before')
    @classmethod
    def normalize_date_values(cls, value):
        if isinstance(value, str):
            value = value.strip()
            for fmt in ("%Y-%m-%d","%m/%d/%Y","%d/%m/%Y","%d-%m-%Y"):
                try:
                    return datetime.strptime(value, fmt).date() 
                except ValueError:
                    continue
            raise ValueError(f"Unsupported date format: {value!r}")

class invoiceData(BaseModel):
    invoice_number: fieldValues[str] 
    invoice_date: dateValues 
    total_amount: fieldValues[float] 

