from dotenv import load_dotenv
from google import genai
import os

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

print("API Key Found:", bool(api_key))

client = genai.Client(
    api_key=api_key
)

try:
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents="Say hello"
    )

    print("✅ Gemini Connection Successful")
    print(response.text)

except Exception as e:
    print("❌ Error:", e)