from fastapi import Depends, FastAPI, HTTPException

from sqlalchemy import func
from sqlalchemy.orm import Session

from connect import SessionLocal
from models import AuditLog, Transaction


app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/transactions/{user_id}/summary")
async def get_transaction_summary(user_id: int, db: Session = Depends(get_db)):

    total_transactions = db.query(func.count(Transaction.id)).filter(Transaction.user_id == user_id).scalar()
    total_amount = db.query(func.sum(Transaction.amount)).filter(Transaction.user_id == user_id).scalar()
    average_transaction_amount = db.query(func.avg(Transaction.amount)).filter(Transaction.user_id == user_id).scalar()
    
    if total_transactions is None or total_transactions == 0:
        raise HTTPException(status_code=404, detail=f"No transactions found for user ID {user_id}")

    log_entry = AuditLog(event=f"Fetched summary for user_id {user_id}")
    db.add(log_entry)
    db.commit()

    return {
        "user_id": user_id,
        "total_transactions": total_transactions,
        "total_amount": total_amount if total_amount else 0,
        "average_transaction_amount": round(average_transaction_amount, 2) if average_transaction_amount else 0
    }
