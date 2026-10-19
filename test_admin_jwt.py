from medical_mcp.auth.jwt_handler import create_access_token

# Replace with your actual admin account ID
ADMIN_ID = 1

token = create_access_token(
    user_id=ADMIN_ID,
    role="admin"
)

print("Admin JWT generated successfully")
print("Token length:", len(token))