import os
from typing import Any

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from app.config import settings
from app.db import get_db
from app.models_db import AuditLog, User

app = FastAPI(title="Hermes Admin API", version="0.2.0")


@app.get("/admin/users")
def list_users(db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    users = db.query(User).all()
    return [{"id": str(u.id), "email": u.email, "username": u.username, "role": u.role} for u in users]


@app.get("/admin/users/{user_id}")
def get_user(user_id: str, db: Session = Depends(get_db)) -> dict[str, Any]:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"id": str(user.id), "email": user.email, "username": user.username, "role": user.role}


@app.put("/admin/users/{user_id}/role")
def update_user_role(user_id: str, payload: dict, db: Session = Depends(get_db)) -> dict[str, str]:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    role = payload.get("role")
    if role not in ["user", "admin", "moderator"]:
        raise HTTPException(status_code=400, detail="Invalid role")

    user.role = role
    db.commit()
    return {"id": str(user.id), "role": role}


@app.get("/admin/audit-logs")
def list_audit_logs(db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    logs = db.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(100).all()
    return [
        {
            "id": str(log.id),
            "user_id": str(log.user_id),
            "action": log.action,
            "resource_type": log.resource_type,
            "created_at": log.created_at.isoformat(),
        }
        for log in logs
    ]
