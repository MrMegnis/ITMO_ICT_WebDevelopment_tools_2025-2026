from datetime import datetime
from enum import Enum
from typing import List, Optional

from sqlmodel import Field, Relationship, SQLModel


class TransactionType(str, Enum):
    income = "income"
    expense = "expense"


class TransactionTagLink(SQLModel, table=True):
    transaction_id: Optional[int] = Field(
        default=None,
        foreign_key="transaction.id",
        primary_key=True,
    )
    tag_id: Optional[int] = Field(
        default=None,
        foreign_key="tag.id",
        primary_key=True,
    )
    added_by: str = Field(default="manual", max_length=50)
    level: int | None = Field(default=None)


class CategoryBase(SQLModel):
    title: str = Field(min_length=1, max_length=100)
    description: str = Field(default="", max_length=255)


class Category(CategoryBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    transactions: List["Transaction"] = Relationship(back_populates="category")


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(SQLModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, max_length=255)


class CategoryRead(CategoryBase):
    id: int


class TagBase(SQLModel):
    name: str = Field(min_length=1, max_length=50)


class Tag(TagBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    transactions: List["Transaction"] = Relationship(
        back_populates="tags",
        link_model=TransactionTagLink,
    )


class TagCreate(TagBase):
    pass


class TagUpdate(SQLModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=50)


class TagRead(TagBase):
    id: int


class TransactionBase(SQLModel):
    amount: float = Field(gt=0)
    transaction_type: TransactionType
    note: str = Field(default="", max_length=255)
    occurred_at: datetime = Field(default_factory=datetime.utcnow)
    category_id: Optional[int] = Field(default=None, foreign_key="category.id")


class Transaction(TransactionBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    category: Optional[Category] = Relationship(back_populates="transactions")
    tags: List[Tag] = Relationship(back_populates="transactions", link_model=TransactionTagLink)


class TransactionCreate(TransactionBase):
    tag_ids: List[int] = Field(default_factory=list)


class TransactionUpdate(SQLModel):
    amount: Optional[float] = Field(default=None, gt=0)
    transaction_type: Optional[TransactionType] = None
    note: Optional[str] = Field(default=None, max_length=255)
    occurred_at: Optional[datetime] = None
    category_id: Optional[int] = None
    tag_ids: Optional[List[int]] = None


class TransactionRead(TransactionBase):
    id: int


class TransactionReadWithRelations(TransactionRead):
    category: Optional[CategoryRead] = None
    tags: List[TagRead] = Field(default_factory=list)
