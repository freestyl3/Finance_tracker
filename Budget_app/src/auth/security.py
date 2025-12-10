import datetime as dt
import bcrypt
import jwt

from src.core.config import settings

def get_password_hash(password: str) -> str:
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_bytes = bcrypt.hashpw(pwd_bytes, salt)
    return hashed_bytes.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    pwd_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(pwd_bytes, hashed_bytes)

def create_access_token(data: dict) -> str:
    to_encode = data.copy()

    expire = dt.datetime.now(dt.timezone.utc) + \
        dt.timedelta(minutes=settings.auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode,
        settings.auth.SECRET_KEY,
        algorithm=settings.auth.ALGORITHM
    )

    return encoded_jwt

def decode_access_token(token: str) -> dict | None:
    try:
        payload = jwt.decode(
            token,
            settings.auth.SECRET_KEY,
            algorithms=[settings.auth.ALGORITHM]
        )
        return payload
    except jwt.PyJWTError:
        return None
