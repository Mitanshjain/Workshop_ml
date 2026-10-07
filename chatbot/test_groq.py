from chatbot_logic import chat_with_patient


message = "I have stomach pain."

response = chat_with_patient(message)

print("Patient:")
print(message)

print("\nChatbot:")
print(response)