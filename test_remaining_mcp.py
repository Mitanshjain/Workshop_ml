
"""
SANJEEVANI — REMAINING MCP SERVER TESTS

Tests admin MCP servers on ports 8006–8010.
Uses read-only tools; no database records are modified.

Run:
    uv run python test_remaining_mcp.py
"""

import asyncio
import subprocess
import sys
from pathlib import Path

from fastmcp import Client
from medical_mcp.auth.jwt_handler import create_access_token


ROOT = Path(__file__).resolve().parent

SERVERS = [
    (
        8006,
        "medical_mcp.servers.admin.doctor_management_mcp",
        "view_all_doctors",
        {},
    ),
    (
        8007,
        "medical_mcp.servers.admin.appointment_management_mcp",
        "view_all_appointments",
        {},
    ),
    (
        8008,
        "medical_mcp.servers.admin.analytics_mcp",
        "view_clinic_analytics",
        {},
    ),
    (
        8009,
        "medical_mcp.servers.admin.authentication_mcp",
        "verify_admin_access",
        {},
    ),
    (
        8010,
        "medical_mcp.servers.admin.security_audit_mcp",
        "view_audit_logs",
        {"limit": 1},
    ),
]


async def probe(port, token, tool_name, arguments):
    """Connect to an MCP server and call a read-only tool."""

    async with Client(
        f"http://127.0.0.1:{port}/mcp",
        auth=token,
    ) as client:

        available_tools = {
            tool.name for tool in await client.list_tools()
        }

        if tool_name not in available_tools:
            raise RuntimeError(
                f"Tool {tool_name} not found. "
                f"Available: {sorted(available_tools)}"
            )

        result = await client.call_tool(
            tool_name,
            arguments,
        )

        if getattr(result, "is_error", False):
            raise RuntimeError("MCP tool returned an error.")

        return result.data


async def main():

    admin_token = create_access_token(
        user_id=1,
        role="admin",
    )

    user_token = create_access_token(
        user_id=1,
        role="user",
    )

    started_servers = []
    passed = 0

    try:

        for port, module, tool_name, arguments in SERVERS:

            print(f"\n{'=' * 50}")
            print(f"TESTING MCP SERVER: {port}")
            print(f"{'=' * 50}")

            # Check whether the server is already running.
            try:
                reader, writer = await asyncio.open_connection(
                    "127.0.0.1",
                    port,
                )

                writer.close()
                await writer.wait_closed()

                print("Existing server detected.")

            except OSError:

                # Start the server automatically.
                log_file = open(
                    ROOT / f"mcp_smoke_{port}.log",
                    "w",
                    encoding="utf-8",
                )

                process = subprocess.Popen(
                    [sys.executable, "-m", module],
                    cwd=ROOT,
                    stdout=log_file,
                    stderr=subprocess.STDOUT,
                )

                started_servers.append(
                    (process, log_file)
                )

                print(f"Starting server on port {port}...")

                await asyncio.sleep(2)

            try:

                # ======================================
                # TEST 1 — ADMIN ACCESS
                # ======================================

                admin_result = None

                for attempt in range(8):
                    try:
                        admin_result = await probe(
                            port,
                            admin_token,
                            tool_name,
                            arguments,
                        )
                        break

                    except Exception:
                        if attempt == 7:
                            raise

                        await asyncio.sleep(1)

                if (
                    not isinstance(admin_result, dict)
                    or admin_result.get("success") is False
                ):
                    raise RuntimeError(
                        f"Admin tool failed: {str(admin_result)[:180]}"
                    )

                print("PASS: Admin read-only access")
                passed += 1

                # ======================================
                # TEST 2 — NORMAL USER ACCESS DENIED
                # ======================================

                try:
                    user_result = await probe(
                        port,
                        user_token,
                        tool_name,
                        arguments,
                    )

                    if (
                        isinstance(user_result, dict)
                        and user_result.get("success") is False
                    ):
                        print("PASS: Normal user access denied")
                        passed += 1

                    else:
                        print(
                            "FAIL: Normal user was not denied!"
                        )

                except Exception as exc:
                    # An authentication/authorization rejection
                    # can happen before a tool returns data.
                    print(
                        "User request rejected or failed:",
                        type(exc).__name__,
                    )
                    print(
                        "Review server logs to confirm "
                        "the rejection was authorization-related."
                    )

            except Exception as exc:

                print(
                    f"FAIL on port {port}: "
                    f"{type(exc).__name__}: {exc}"
                )

        print("\n" + "=" * 50)
        print("FINAL TEST RESULT")
        print("=" * 50)

        print(f"Passed: {passed}/10")

        if passed == 10:
            print("ALL CHECKS PASSED!")
        else:
            print("Some checks need review.")

        print("No write tools were called.")

    finally:

        # Stop only servers started by this script.
        for process, log_file in started_servers:

            process.terminate()

            try:
                process.wait(timeout=5)

            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()

            log_file.close()


if __name__ == "__main__":
    asyncio.run(main())
