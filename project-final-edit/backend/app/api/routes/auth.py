import re
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import User
from app.schemas import RegisterInput, LoginInput
from app.core.security import hash_password, verify_password, create_access_token, get_current_user

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])

def normalize_email(email: str) -> str:
    return email.strip().lower()

def public_user(user: User) -> dict:
    return {"id": user.id, "full_name": user.full_name, "email": user.email,
            "created_at": user.created_at.isoformat() if user.created_at else None}

@router.post("/register", status_code=201)
def register(payload: RegisterInput, db: Session = Depends(get_db)):
    email = normalize_email(payload.email)
    if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email):
        raise HTTPException(status_code=422, detail="Enter a valid email address.")
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=409, detail="An account with this email already exists.")
    full_name = payload.full_name.strip()
    if len(full_name) < 2:
        raise HTTPException(status_code=422, detail="Full name must contain at least 2 non-space characters.")
    user = User(full_name=full_name, email=email, password_hash=hash_password(payload.password))
    db.add(user)
    try:
        db.commit(); db.refresh(user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="An account with this email already exists.")
    return {"access_token": create_access_token(user.id), "token_type": "bearer", "user": public_user(user)}

@router.post("/login")
def login(payload: LoginInput, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == normalize_email(payload.email)).first()
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect email or password.")
    return {"access_token": create_access_token(user.id), "token_type": "bearer", "user": public_user(user)}

@router.get("/me")
def me(user: User = Depends(get_current_user)):
    return public_user(user)
