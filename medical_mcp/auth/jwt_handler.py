
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import jwt
from dotenv import load_dotenv

from src.logger import get_logger
from src.exception import CustomException


# ==========================================
# LOAD ENVIRONMENT VARIABLES
# ==========================================

load_dotenv(
    Path(__file__).resolve().parents[1] / ".env"
)

logger = get_logger(__name__)

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = "HS256"
EXPIRY_MINUTES = int(
    os.getenv("JWT_EXPIRY_MINUTES", "30")
)

if not SECRET_KEY:
    raise RuntimeError(
        "JWT_SECRET_KEY is missing in medical_mcp/.env"
    )


# ==========================================
# GENERATE JWT TOKEN
# ==========================================

def create_access_token(user_id: int, role: str):

    try:
        expiration = datetime.now(timezone.utc) + timedelta(
            minutes=EXPIRY_MINUTES
        )

        payload = {
            "sub": str(user_id),
            "role": role,
            "exp": expiration
        }

        token = jwt.encode(
            payload,
            SECRET_KEY,
            algorithm=ALGORITHM
        )

        logger.info("JWT token generated successfully")

        return token

    except Exception as e:
        logger.error(f"JWT generation failed: {e}")
        raise CustomException(e, sys)


# ==========================================
# VERIFY JWT TOKEN
# ==========================================

def verify_access_token(token: str):

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
            options={"require": ["sub", "role", "exp"]}
        )

        logger.info("JWT token verified successfully")

        return payload

    except jwt.ExpiredSignatureError:
        logger.warning("JWT token has expired")
        return None

    except jwt.InvalidTokenError:
        logger.warning("Invalid JWT token")
        return None

    except Exception as e:
        logger.error(f"JWT verification failed: {e}")
        raise CustomException(e, sys)
