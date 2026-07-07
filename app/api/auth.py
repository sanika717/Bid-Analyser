from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr

from app.auth import authenticate_user, create_auth_token, create_user, create_password_reset, get_password_reset, mark_password_reset_used, update_password_hash, require_auth, get_user, send_password_reset_email
from app.core.config import PASSWORD_RESET_URL

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    remember_me: bool = False


class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str


class ForgotRequest(BaseModel):
    email: EmailStr


class ResetRequest(BaseModel):
    token: str
    password: str


@router.post("/login")
def login(payload: LoginRequest):
    user = authenticate_user(payload.email, payload.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    expires = 30 if payload.remember_me else 8
    token = create_auth_token(user["email"], user["name"], user["role"], hours=expires)
    return {"access_token": token, "token_type": "bearer", "user": {"email": user["email"], "name": user["name"], "role": user["role"]}}


@router.post("/register")
def register(payload: RegisterRequest):
    if get_user(payload.email):
        raise HTTPException(status_code=400, detail="User already exists")
    create_user(payload.email, payload.password, payload.name)
    return {"message": "Registration successful"}


@router.post("/forgot")
def forgot_password(payload: ForgotRequest):
    user = get_user(payload.email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    reset_token = create_password_reset(payload.email)
    send_password_reset_email(payload.email, reset_token)
    return {"message": "Password reset email queued. Check storage/emails for running environment logs."}


@router.post("/reset")
def reset_password(payload: ResetRequest):
    reset = get_password_reset(payload.token)
    if not reset or reset["used"] or reset["expires_at"] < datetime.now(timezone.utc).isoformat():
        raise HTTPException(status_code=400, detail="Reset token is invalid or expired")
    update_password_hash(reset["email"], payload.password)
    mark_password_reset_used(payload.token)
    return {"message": "Password updated"}


@router.get("/me")
def me(user=Depends(require_auth)):
    return {"user": {"email": user["email"], "name": user["name"], "role": user["role"]}}
