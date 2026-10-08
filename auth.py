from datetime import datetime
from datetime import timedelta
from datetime import timezone

from fastapi import Depends
from fastapi import HTTPException
from fastapi import status

from fastapi.security import OAuth2PasswordBearer

from jose import JWTError
from jose import jwt

from pwdlib import PasswordHash

from sqlalchemy.orm import Session

from database import get_db
from models import User


# =========================
# JWT SETTINGS
# =========================

SECRET_KEY = "change-this-secret-key-in-production"

ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 60


# =========================
# PASSWORD HASHING
# =========================

password_hash = PasswordHash.recommended()


# =========================
# OAUTH2 BEARER
# =========================

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/login"
)


# =========================
# HASH PASSWORD
# =========================

def hash_password(password: str):

    return password_hash.hash(password)


# =========================
# VERIFY PASSWORD
# =========================

def verify_password(
    plain_password: str,
    hashed_password: str
):

    return password_hash.verify(
        plain_password,
        hashed_password
    )


# =========================
# CREATE JWT ACCESS TOKEN
# =========================

def create_access_token(data: dict):

    to_encode = data.copy()

    expire = (
        datetime.now(timezone.utc)
        + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )
    )

    to_encode.update({
        "exp": expire
    })

    encoded_jwt = jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return encoded_jwt


# =========================
# AUTHENTICATE USER
# =========================

def authenticate_user(
    db: Session,
    email: str,
    password: str
):

    user = db.query(User).filter(
        User.email == email
    ).first()

    if not user:
        return None

    if not verify_password(
        password,
        user.password
    ):
        return None

    return user


# =========================
# GET CURRENT USER
# =========================

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
        headers={
            "WWW-Authenticate": "Bearer"
        }
    )

    try:

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        user_id = payload.get("sub")

        if user_id is None:
            raise credentials_exception

        user_id = int(user_id)

    except (JWTError, ValueError):

        raise credentials_exception

    user = db.query(User).filter(
        User.id == user_id
    ).first()

    if user is None:
        raise credentials_exception

    return user
