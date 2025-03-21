from pydantic import BaseModel, Field
from typing import Optional
from datetime import date


# Base class for common fields
class Expense(BaseModel):
   name: str
   amount: float
   date: date
   category: str

