
from medical_mcp.auth.jwt_handler import (
    create_access_token,
    verify_access_token
)

from src.logger import get_logger

logger = get_logger(__name__)


# ==========================================
# TEST 1: GENERATE JWT TOKEN
# ==========================================

# Sample user for testing only
user_id = 1
role = "user"

token = create_access_token(
    user_id=user_id,
    role=role
)

logger.info("JWT token generated for test user")

print("\nJWT Token Generated Successfully")


# ==========================================
# TEST 2: VERIFY VALID JWT TOKEN
# ==========================================

payload = verify_access_token(token)

print("\nTEST 2: Valid JWT Token")
print("Payload:", payload)

assert payload is not None
assert payload["sub"] == "1"
assert payload["role"] == "user"

print("Valid token test passed!")


# ==========================================
# TEST 3: VERIFY INVALID JWT TOKEN
# ==========================================

invalid_token = token + "invalid"

invalid_payload = verify_access_token(
    invalid_token
)

print("\nTEST 3: Invalid JWT Token")
print("Payload:", invalid_payload)

assert invalid_payload is None

print("Invalid token test passed!")


# ==========================================
# FINAL RESULT
# ==========================================

print("\nAll JWT tests passed successfully!")
