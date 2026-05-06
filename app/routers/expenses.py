from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..auth import get_current_user
from ..database import get_db
from ..models import Expense, User
from ..schemas import ExpenseCreate, ExpensePublic

router = APIRouter(prefix="/expenses", tags=["Expenses"])


@router.get("", response_model=list[ExpensePublic])
def list_expenses(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return (
        db.query(Expense)
        .filter(Expense.user_id == current_user.id)
        .order_by(Expense.spent_on.desc(), Expense.id.desc())
        .all()
    )


@router.post("", response_model=ExpensePublic, status_code=201)
def add_expense(payload: ExpenseCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    expense = Expense(
        user_id=current_user.id,
        title=payload.title,
        category=payload.category,
        amount=payload.amount,
        spent_on=payload.spent_on or date.today(),
        notes=payload.notes,
    )
    db.add(expense)
    db.commit()
    db.refresh(expense)
    return expense


@router.delete("/{expense_id}", status_code=204)
def delete_expense(expense_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    expense = db.query(Expense).filter(Expense.id == expense_id, Expense.user_id == current_user.id).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    db.delete(expense)
    db.commit()
    return None

