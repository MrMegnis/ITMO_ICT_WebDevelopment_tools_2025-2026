from datetime import date, datetime
from typing import Optional

from pydantic import EmailStr
from sqlmodel import Field, SQLModel

from .models import TransactionType


class UserRegister(SQLModel):
    email: EmailStr
    username: str = Field(min_length=3, max_length=100)
    password: str = Field(min_length=6, max_length=128)


class UserRead(SQLModel):
    id: int
    email: EmailStr
    username: str
    created_at: datetime


class TokenRead(SQLModel):
    access_token: str
    token_type: str = "bearer"


class PasswordChange(SQLModel):
    old_password: str = Field(min_length=6, max_length=128)
    new_password: str = Field(min_length=6, max_length=128)


class CategoryBase(SQLModel):
    title: str = Field(min_length=1, max_length=100)
    description: str = Field(default="", max_length=255)


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(SQLModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, max_length=255)


class CategoryRead(CategoryBase):
    id: int


class TagBase(SQLModel):
    name: str = Field(min_length=1, max_length=50)


class TagCreate(TagBase):
    pass


class TagUpdate(SQLModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=50)


class TagRead(TagBase):
    id: int


class TransactionTagAssign(SQLModel):
    tag_id: int
    importance: int = Field(default=1, ge=1, le=5)
    tagged_reason: str = Field(default="manual", max_length=100)


class TransactionBase(SQLModel):
    amount: float = Field(gt=0)
    transaction_type: TransactionType
    note: str = Field(default="", max_length=255)
    occurred_at: datetime = Field(default_factory=datetime.utcnow)
    category_id: Optional[int] = None


class TransactionCreate(TransactionBase):
    tags: list[TransactionTagAssign] = Field(default_factory=list)


class TransactionUpdate(SQLModel):
    amount: Optional[float] = Field(default=None, gt=0)
    transaction_type: Optional[TransactionType] = None
    note: Optional[str] = Field(default=None, max_length=255)
    occurred_at: Optional[datetime] = None
    category_id: Optional[int] = None
    tags: Optional[list[TransactionTagAssign]] = None


class TransactionTagRead(SQLModel):
    id: int
    name: str
    importance: int
    tagged_reason: str


class TransactionRead(TransactionBase):
    id: int
    category: Optional[CategoryRead] = None
    tags: list[TransactionTagRead] = Field(default_factory=list)


class BudgetBase(SQLModel):
    limit_amount: float = Field(gt=0)
    start_date: date
    end_date: date
    category_id: int


class BudgetCreate(BudgetBase):
    pass


class BudgetUpdate(SQLModel):
    limit_amount: Optional[float] = Field(default=None, gt=0)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    category_id: Optional[int] = None


class BudgetRead(BudgetBase):
    id: int
    category: CategoryRead


class GoalBase(SQLModel):
    title: str = Field(min_length=1, max_length=150)
    target_amount: float = Field(gt=0)
    current_amount: float = Field(default=0, ge=0)
    deadline: Optional[date] = None


class GoalCreate(GoalBase):
    pass


class GoalUpdate(SQLModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=150)
    target_amount: Optional[float] = Field(default=None, gt=0)
    current_amount: Optional[float] = Field(default=None, ge=0)
    deadline: Optional[date] = None


class GoalRead(GoalBase):
    id: int


class ReportSummary(SQLModel):
    total_income: float
    total_expense: float
    balance: float
    budgets_exceeded: int


class ParsedSourceRead(SQLModel):
    id: int
    url: str
    title: str
    source: str
    elapsed: float
    created_at: datetime
