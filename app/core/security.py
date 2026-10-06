import jwt
from typing import Optional
from datetime import datetime, timedelta, timezone
from jwt import InvalidTokenError
from fastapi import status, Depends, HTTPException

from app.core.config import ACCESS_TOKEN, ALGORITHM, SECRET_KEY


def create_access_token(
    data: dict, 
    expires_delta: Optional[timedelta] = None
) -> str:
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN)
    )

    to_encode.update({"exp": expire})

    return jwt.encode(
                to_encode,
                SECRET_KEY,
                algorithm=ALGORITHM
            )


def verify_access_token(token : str):
        try:
            payload = jwt.decode(
                 token,
                 SECRET_KEY,
                 algorithms=ALGORITHM
            )
            return payload
        
        except InvalidTokenError:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token"
                )
             
