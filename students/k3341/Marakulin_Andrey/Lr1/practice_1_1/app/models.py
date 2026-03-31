from enum import Enum
from typing import List

from pydantic import BaseModel, Field


class TransactionType(str, Enum):
    income = "income"
    expense = "expense"


class Category(BaseModel):
    id: int
    title: str = Field(min_length=1, max_length=100)
    description: str = ""


class Tag(BaseModel):
    id: int
    name: str = Field(min_length=1, max_length=50)


class Transaction(BaseModel):
    id: int
    amount: float = Field(gt=0)
    transaction_type: TransactionType
    note: str = ""
    category: Category
    tags: List[Tag] = Field(default_factory=list)
