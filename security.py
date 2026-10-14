from pwdlib import PasswordHash
import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from datetime import datetime,timedelta,timezone
from config import settings

JWT_KEY = settings.JWT_SECRET_KEY
JWT_TOKEN_EXPIRE_MINUTES = settings.JWT_TOKEN_EXPIRE_MINUTES
ALGORITHM = "HS256"

password_hash = PasswordHash.recommended()

def create_token(data):
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(data.id),
        "iat": now,
        "exp": now + timedelta(minutes=JWT_TOKEN_EXPIRE_MINUTES)
    }

    token = jwt.encode(payload, JWT_KEY, ALGORITHM)

    return token

def decode_token(token):
    try:
        payload = jwt.decode(
            token,
            JWT_KEY,
            algorithms=[ALGORITHM]
        )
        return payload

    except ExpiredSignatureError as e:
        print("TOKEN SCADUTO:", e)
        return None

    except InvalidTokenError as e:
        print("TOKEN NON VALIDO:", type(e).__name__, e)
        return None