
# ==========================================
# SANJEEVANI - MEDICAL LLM MCP SERVER
# ==========================================

import logging
from pathlib import Path
import sys

from fastmcp import FastMCP
from fastmcp.server.auth.providers.jwt import JWTVerifier
from fastmcp.server.dependencies import get_access_token

# ==========================================
# PROJECT ROOT
# ==========================================

PROJECT_ROOT = Path(__file__).resolve().parents[3]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# ==========================================
# EXISTING GROQ CLIENT
# ==========================================

from chatbot.groq_client import ask_groq
from medical_mcp.auth.rbac import check_permission

# ==========================================
# LOGGING
# ==========================================

logger = logging.getLogger(__name__)

# ==========================================
# JWT AUTHENTICATION
# ==========================================

import os
from dotenv import load_dotenv

load_dotenv(PROJECT_ROOT / "medical_mcp" / ".env")

JWT_SECRET = os.getenv("JWT_SECRET_KEY")

if not JWT_SECRET:
    raise RuntimeError("JWT_SECRET_KEY is missing.")

auth = JWTVerifier(
    public_key=JWT_SECRET,
    algorithm="HS256"
)

# ==========================================
# FASTMCP SERVER
# ==========================================

mcp = FastMCP(
    "Medical LLM MCP Server",
    auth=auth
)

# ==========================================
# MEDICAL LLM TOOL
# ==========================================

@mcp.tool()
def medical_llm_chat(message: str) -> dict:

    token = get_access_token()

    if token is None:
        return {
            "success": False,
            "message": "Authentication required."
        }

    role = token.claims.get("role")

    # Basic role restriction
    if role not in ("user", "admin"):
        return {
            "success": False,
            "message": "Access denied."
        }

    if not message or not message.strip():
        return {
            "success": False,
            "message": "Please enter a message."
        }

    if len(message) > 2000:
        return {
            "success": False,
            "message": "Message is too long."
        }

    try:
        # Reuse existing Groq integration
        response = ask_groq([
            {
                "role": "user",
                "content": message.strip()
            }
        ])

        return {
            "success": True,
            "response": response
        }

    except Exception:
        logger.exception("Medical LLM request failed.")

        return {
            "success": False,
            "message": "Medical LLM service is unavailable."
        }


# ==========================================
# RUN SERVER
# ==========================================

if __name__ == "__main__":
    mcp.run(
        transport="http",
        host="127.0.0.1",
        port=8004
    )
