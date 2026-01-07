from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt 
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from api.database import get_db
from api.models import User

SECRET_KEY = "chave"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl = "/api/v1/auth/login")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated = "auto")

def get_password_hash(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password:str, hashed_password:str):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes = ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try: 
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code = 401, detail="Invalid Token")
    except:
        raise HTTPException(status_code=401, detail="Invalid Token")
    
    user = db.query(User).filter(User.user_name == username).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    
    return user

router = APIRouter()


@router.post("/auth/register")
def register(username: str, password: str, db: Session = Depends(get_db)):
    new_user = User(user_name = username, password_hash = get_password_hash(password))
    db.add(new_user)
    db.commit()
    return {"username": username , "created": True}



@router.post("/auth/login")
def login(username: str, password: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.user_name == username).first()
    
    if user:
        user_hash = user.password_hash
        if verify_password(password, user_hash):
            return create_access_token({"sub": username})
        else:
            raise HTTPException(status_code = 401, detail="Invalid Credentials")
    else:
        raise HTTPException(status_code = 401, detail="Invalid Credentials")
    

@router.post("/auth/refresh")
def refresh_token(current_user: User = Depends(get_current_user)):
    return create_access_token({"sub": current_user.user_name})

