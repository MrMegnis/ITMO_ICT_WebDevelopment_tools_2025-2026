from datetime import UTC, date, datetime, timedelta

from sqlmodel import Session, select

from app.core.security import hash_password
from app.db import engine
from app.models import (
    Budget,
    Category,
    Goal,
    Tag,
    Transaction,
    TransactionTagLink,
    TransactionType,
    User,
)


def get_or_create_demo_user(session: Session) -> User:
    user = session.exec(select(User).where(User.username == "demo")).first()
    if user:
        return user

    user = User(
        email="demo@example.com",
        username="demo",
        hashed_password=hash_password("demo12345"),
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def ensure_categories(session: Session, user_id: int) -> dict[str, Category]:
    wanted = {
        "Salary": "Monthly salary income",
        "Food": "Groceries and restaurants",
        "Transport": "Public transport and taxi",
    }
    existing = session.exec(select(Category).where(Category.user_id == user_id)).all()
    by_title = {item.title: item for item in existing}

    for title, description in wanted.items():
        if title not in by_title:
            obj = Category(title=title, description=description, user_id=user_id)
            session.add(obj)
            session.commit()
            session.refresh(obj)
            by_title[title] = obj

    return by_title


def ensure_tags(session: Session, user_id: int) -> dict[str, Tag]:
    wanted = ["required", "monthly", "urgent", "planned"]
    existing = session.exec(select(Tag).where(Tag.user_id == user_id)).all()
    by_name = {item.name: item for item in existing}

    for name in wanted:
        if name not in by_name:
            obj = Tag(name=name, user_id=user_id)
            session.add(obj)
            session.commit()
            session.refresh(obj)
            by_name[name] = obj

    return by_name


def ensure_transactions(
    session: Session,
    user_id: int,
    categories: dict[str, Category],
    tags: dict[str, Tag],
) -> None:
    exists = session.exec(select(Transaction).where(Transaction.user_id == user_id)).first()
    if exists:
        return

    now = datetime.now(UTC).replace(tzinfo=None)
    salary_tx = Transaction(
        amount=120000,
        transaction_type=TransactionType.income,
        note="Salary for current month",
        occurred_at=now - timedelta(days=7),
        user_id=user_id,
        category_id=categories["Salary"].id,
    )
    food_tx = Transaction(
        amount=14500,
        transaction_type=TransactionType.expense,
        note="Groceries and takeout",
        occurred_at=now - timedelta(days=3),
        user_id=user_id,
        category_id=categories["Food"].id,
    )
    transport_tx = Transaction(
        amount=4200,
        transaction_type=TransactionType.expense,
        note="Metro and taxi",
        occurred_at=now - timedelta(days=1),
        user_id=user_id,
        category_id=categories["Transport"].id,
    )

    session.add(salary_tx)
    session.add(food_tx)
    session.add(transport_tx)
    session.commit()
    session.refresh(salary_tx)
    session.refresh(food_tx)
    session.refresh(transport_tx)

    links = [
        TransactionTagLink(
            transaction_id=salary_tx.id,
            tag_id=tags["monthly"].id,
            importance=5,
            tagged_reason="Main source of income",
        ),
        TransactionTagLink(
            transaction_id=food_tx.id,
            tag_id=tags["required"].id,
            importance=4,
            tagged_reason="Essential expense",
        ),
        TransactionTagLink(
            transaction_id=transport_tx.id,
            tag_id=tags["planned"].id,
            importance=3,
            tagged_reason="Regular weekly spending",
        ),
    ]
    for link in links:
        session.add(link)
    session.commit()


def ensure_budget_and_goal(session: Session, user_id: int, categories: dict[str, Category]) -> None:
    budget_exists = session.exec(select(Budget).where(Budget.user_id == user_id)).first()
    if not budget_exists:
        budget = Budget(
            limit_amount=20000,
            start_date=date.today().replace(day=1),
            end_date=date.today(),
            user_id=user_id,
            category_id=categories["Food"].id,
        )
        session.add(budget)
        session.commit()

    goal_exists = session.exec(select(Goal).where(Goal.user_id == user_id)).first()
    if not goal_exists:
        goal = Goal(
            title="Laptop fund",
            target_amount=150000,
            current_amount=45000,
            deadline=date.today() + timedelta(days=180),
            user_id=user_id,
        )
        session.add(goal)
        session.commit()


def main() -> None:
    with Session(engine) as session:
        user = get_or_create_demo_user(session)
        categories = ensure_categories(session, user.id)
        tags = ensure_tags(session, user.id)
        ensure_transactions(session, user.id, categories, tags)
        ensure_budget_and_goal(session, user.id, categories)
    print("Seed completed. Demo user: demo / demo12345")


if __name__ == "__main__":
    main()
