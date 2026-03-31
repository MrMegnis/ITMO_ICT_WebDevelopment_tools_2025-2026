from datetime import datetime, time

from fastapi import APIRouter, Depends
from sqlmodel import Session, and_, select

from app.db import get_session
from app.dependencies import get_current_user
from app.models import Budget, Transaction, TransactionType, User
from app.schemas import ReportSummary

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/summary", response_model=ReportSummary)
def report_summary(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> ReportSummary:
    transactions = session.exec(
        select(Transaction).where(Transaction.user_id == current_user.id),
    ).all()

    total_income = sum(item.amount for item in transactions if item.transaction_type == TransactionType.income)
    total_expense = sum(item.amount for item in transactions if item.transaction_type == TransactionType.expense)

    budgets = session.exec(select(Budget).where(Budget.user_id == current_user.id)).all()
    exceeded = 0
    for budget in budgets:
        start_dt = datetime.combine(budget.start_date, time.min)
        end_dt = datetime.combine(budget.end_date, time.max)
        spent = session.exec(
            select(Transaction).where(
                and_(
                    Transaction.user_id == current_user.id,
                    Transaction.category_id == budget.category_id,
                    Transaction.transaction_type == TransactionType.expense,
                    Transaction.occurred_at >= start_dt,
                    Transaction.occurred_at <= end_dt,
                ),
            ),
        ).all()
        total_spent = sum(item.amount for item in spent)
        if total_spent > budget.limit_amount:
            exceeded += 1

    return ReportSummary(
        total_income=total_income,
        total_expense=total_expense,
        balance=total_income - total_expense,
        budgets_exceeded=exceeded,
    )
