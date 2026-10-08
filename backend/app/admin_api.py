import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import require_api_key
from app.db import get_db
from app.models_db import AuditLog, User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/users")
async def list_users(admin_id: str = Depends(require_api_key), db: Session = Depends(get_db)) -> list[dict]:
    """List all users (admin only)"""
    admin_user = db.query(User).filter(User.id == admin_id).first()
    if not admin_user or admin_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    users = db.query(User).all()
    return [
        {
            "id": str(u.id),
            "email": u.email,
            "username": u.username,
            "role": u.role,
            "created_at": u.created_at.isoformat(),
        }
        for u in users
    ]


@router.put("/users/{user_id}/role")
async def update_user_role(
    user_id: str,
    payload: dict,
    admin_id: str = Depends(require_api_key),
    db: Session = Depends(get_db),
) -> dict:
    """Update user role (admin only)"""
    admin_user = db.query(User).filter(User.id == admin_id).first()
    if not admin_user or admin_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    new_role = payload.get("role")
    if new_role not in ["user", "admin"]:
        raise HTTPException(status_code=400, detail="Invalid role")

    user.role = new_role
    db.commit()
    db.refresh(user)

    audit_log = AuditLog(
        user_id=admin_id,
        action="update_user_role",
        resource_type="user",
        resource_id=user_id,
        metadata={"new_role": new_role},
    )
    db.add(audit_log)
    db.commit()

    return {"id": str(user.id), "email": user.email, "role": user.role}


@router.get("/audit-logs")
async def list_audit_logs(
    admin_id: str = Depends(require_api_key), db: Session = Depends(get_db)
) -> list[dict[str, Any]]:
    """List audit logs (admin only)"""
    admin_user = db.query(User).filter(User.id == admin_id).first()
    if not admin_user or admin_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    logs = db.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(100).all()
    return [
        {
            "id": str(log.id),
            "user_id": str(log.user_id) if log.user_id else None,
            "action": log.action,
            "resource_type": log.resource_type,
            "resource_id": log.resource_id,
            "metadata": log.metadata or {},
            "created_at": log.created_at.isoformat(),
        }
        for log in logs
    ]
