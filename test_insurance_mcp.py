import asyncio
from fastmcp import Client
from medical_mcp.auth.jwt_handler import create_access_token


async def main():
    token = create_access_token(user_id=1, role="user")

    async with Client(
        "http://127.0.0.1:8005/mcp",
        auth=token
    ) as client:

        for patient_id in [1, 2]:
            result = await client.call_tool(
                "insurance_details",
                {"patient_id": patient_id}
            )

            data = result.data

            # Do not expose insurance policy numbers
            if isinstance(data, dict):
                data = data.copy()
                insurance = data.get("insurance")

                if isinstance(insurance, dict):
                    data["insurance"] = {
                        **insurance,
                        "policy_number": "[REDACTED]"
                    }

            print(f"Patient {patient_id}: {data}")


if __name__ == "__main__":
    asyncio.run(main())