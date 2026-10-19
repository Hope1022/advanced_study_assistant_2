from passlib.context import CryptContext
from datetime import datetime,timedelta,timezone
from dotenv import load_dotenv
from typing import Any
from jose import JWTError, jwt
from jose.exceptions import ExpiredSignatureError
import os
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES",30))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7))
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(plain_password:str)->str:
    return pwd_context.hash(plain_password)
    
def verify_password(plain_password:str, hashed_password:str) -> bool: 
    return pwd_context.verify(plain_password, hashed_password)
    
def create_access_token(data: dict[str, Any]) -> str:
    to_encode = data.copy()
 
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
 
    to_encode.update({
        "exp": expire,       
        "type": "access"    
    })
 
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
 

def create_refresh_token(data: dict[str, Any]) -> str:
    to_encode = data.copy()
 
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
 
    to_encode.update({
        "exp": expire,
        "type": "refresh"
    })
 
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
 
def decode_token(token: str) -> dict[str, Any] | None:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None



def verify_token_type(payload: dict[str, Any], expected_type: str) -> bool:
    return payload.get("type") == expected_type
 

