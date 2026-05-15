from datetime import date, datetime
from enum import Enum
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel


class TransactionType(str, Enum):
    income = "income"
    expense = "expense"


class User(SQLModel, table=True):
    __tablename__ = "app_user"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True, max_length=255)
    username: str = Field(index=True, unique=True, max_length=100)
    hashed_password: str = Field(max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    categories: list["Category"] = Relationship(back_populates="owner")
    tags: list["Tag"] = Relationship(back_populates="owner")
    transactions: list["Transaction"] = Relationship(back_populates="owner")
    budgets: list["Budget"] = Relationship(back_populates="owner")
    goals: list["Goal"] = Relationship(back_populates="owner")
    parsed_sources: list["ParsedSource"] = Relationship(back_populates="owner")


class Category(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(max_length=100)
    description: str = Field(default="", max_length=255)
    user_id: int = Field(foreign_key="app_user.id", index=True)

    owner: User = Relationship(back_populates="categories")
    transactions: list["Transaction"] = Relationship(back_populates="category")
    budgets: list["Budget"] = Relationship(back_populates="category")


class TransactionTagLink(SQLModel, table=True):
    transaction_id: Optional[int] = Field(
        default=None,
        foreign_key="transaction.id",
        primary_key=True,
    )
    tag_id: Optional[int] = Field(default=None, foreign_key="tag.id", primary_key=True)
    importance: int = Field(default=1, ge=1, le=5)
    tagged_reason: str = Field(default="manual", max_length=100)


class Tag(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=50)
    user_id: int = Field(foreign_key="app_user.id", index=True)

    owner: User = Relationship(back_populates="tags")
    transactions: list["Transaction"] = Relationship(
        back_populates="tags",
        link_model=TransactionTagLink,
    )


class Transaction(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    amount: float = Field(gt=0)
    transaction_type: TransactionType
    note: str = Field(default="", max_length=255)
    occurred_at: datetime = Field(default_factory=datetime.utcnow)

    user_id: int = Field(foreign_key="app_user.id", index=True)
    category_id: Optional[int] = Field(default=None, foreign_key="category.id")

    owner: User = Relationship(back_populates="transactions")
    category: Optional[Category] = Relationship(back_populates="transactions")
    tags: list[Tag] = Relationship(back_populates="transactions", link_model=TransactionTagLink)


class Budget(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    limit_amount: float = Field(gt=0)
    start_date: date
    end_date: date
    user_id: int = Field(foreign_key="app_user.id", index=True)
    category_id: int = Field(foreign_key="category.id")

    owner: User = Relationship(back_populates="budgets")
    category: Category = Relationship(back_populates="budgets")


class Goal(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(max_length=150)
    target_amount: float = Field(gt=0)
    current_amount: float = Field(default=0, ge=0)
    deadline: Optional[date] = None
    user_id: int = Field(foreign_key="app_user.id", index=True)

    owner: User = Relationship(back_populates="goals")


class ParsedSource(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    url: str = Field(max_length=2048)
    title: str = Field(max_length=255)
    source: str = Field(max_length=50)
    elapsed: float = Field(ge=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    user_id: int = Field(foreign_key="app_user.id", index=True)

    owner: User = Relationship(back_populates="parsed_sources")
