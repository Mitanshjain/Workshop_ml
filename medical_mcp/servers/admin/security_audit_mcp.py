
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from fastmcp import FastMCP
from fastmcp.server.auth.providers.jwt import JWTVerifier
from fastmcp.server.dependencies import get_access_token


# ==========================================
# CONFIGURATION
# ==========================================

PROJECT_ROOT = Path(__file__).resolve().parents[3]

load_dotenv(PROJECT_ROOT / "medical_mcp" / ".env")

JWT_SECRET = os.getenv("JWT_SECRET_KEY")

if not JWT_SECRET:
    raise RuntimeError("JWT_SECRET_KEY is missing.")

DB_PATH = PROJECT_ROOT / "medical_mcp" / "clinic.db"


# ==========================================
# AUTHENTICATION
# ==========================================

auth = JWTVerifier(
    public_key=JWT_SECRET,
    algorithm="HS256"
)

mcp = FastMCP(
    "Clinic Security and Audit MCP Server",
    auth=auth
)


# ==========================================
# DATABASE INITIALIZATION
# ==========================================

def initialize_audit_table():

    with sqlite3.connect(DB_PATH) as con:

        con.execute("""
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                actor_id TEXT NOT NULL,
                actor_role TEXT NOT NULL,
                action TEXT NOT NULL,
                details TEXT,
                created_at TEXT NOT NULL
            )
        """)


# ==========================================
# RECORD AUDIT EVENT
# ==========================================

@mcp.tool()
def record_audit_event(
    action: str,
    details: str = ""
) -> dict:

    token = get_access_token()

    if token is None:
        return {
            "success": False,
            "message": "Authentication required."
        }

    role = token.claims.get("role")

    if role != "admin":
        return {
            "success": False,
            "message": "Admin access required."
        }

    action = action.strip()

    if not action or len(action) > 100:
        return {
            "success": False,
            "message": "Invalid action."
        }

    if len(details) > 2000:
        return {
            "success": False,
            "message": "Details too long."
        }

    actor_id = str(token.claims.get("sub", ""))

    if not actor_id:
        return {
            "success": False,
            "message": "Invalid user identity."
        }

    created_at = datetime.now(timezone.utc).isoformat()

    with sqlite3.connect(DB_PATH) as con:

        cursor = con.execute(
            """
            INSERT INTO audit_logs
            (actor_id, actor_role, action, details, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                actor_id,
                role,
                action,
                details,
                created_at
            )
        )

        log_id = cursor.lastrowid

    return {
        "success": True,
        "message": "Audit event recorded.",
        "log_id": log_id
    }


# ==========================================
# VIEW AUDIT HISTORY
# ==========================================

@mcp.tool()
def view_audit_logs(limit: int = 20) -> dict:

    token = get_access_token()

    if token is None:
        return {
            "success": False,
            "message": "Authentication required."
        }

    if token.claims.get("role") != "admin":
        return {
            "success": False,
            "message": "Admin access required."
        }

    limit = max(1, min(limit, 100))

    with sqlite3.connect(DB_PATH) as con:

        con.row_factory = sqlite3.Row

        rows = con.execute(
            """
            SELECT
                id,
                actor_id,
                actor_role,
                action,
                details,
                created_at
            FROM audit_logs
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,)
        ).fetchall()

    return {
        "success": True,
        "total_returned": len(rows),
        "logs": [dict(row) for row in rows]
    }


# ==========================================
# START MCP SERVER
# ==========================================

if __name__ == "__main__":

    initialize_audit_table()

    mcp.run(
        transport="http",
        host="127.0.0.1",
        port=8010
    )
