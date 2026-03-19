from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.user import User
from app.models.api_key import APIKey
from app.schemas.user import UserCreate, UserLogin, UserResponse, Token
from app.auth.password import hash_password, verify_password
from app.auth.jwt import create_access_token
import secrets

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/signup", response_model=Token)
def signup(user_data: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(
        (User.email == user_data.email) | (User.username == user_data.username)
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email or username already exists")

    user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hash_password(user_data.password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    api_key = APIKey(
        user_id=user.id,
        key=f"rl_{secrets.token_urlsafe(32)}",
        name="default"
    )
    db.add(api_key)
    db.commit()
    db.refresh(api_key)

    access_token = create_access_token({"sub": str(user.id), "email": user.email})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "api_key": api_key.key
    }

@router.post("/login", response_model=Token)
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_data.email).first()
    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    api_key = db.query(APIKey).filter(
        APIKey.user_id == user.id,
        APIKey.is_active == True
    ).first()

    access_token = create_access_token({"sub": str(user.id), "email": user.email})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "api_key": api_key.key if api_key else ""
    }

@router.get("/me", response_model=UserResponse)
def get_me(token: str, db: Session = Depends(get_db)):
    from app.auth.jwt import verify_token
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(User).filter(User.id == int(payload["sub"])).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user