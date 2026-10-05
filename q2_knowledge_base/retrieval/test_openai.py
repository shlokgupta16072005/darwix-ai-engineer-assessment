import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    print("[ERROR] OPENAI_API_KEY not found.")
    raise SystemExit(1)

print("[OK] API key loaded.")
print("[OK] Key starts with:", api_key[:7] + "...")


client = OpenAI(api_key=api_key)

try:
    models = client.models.list()
    print("[OK] OpenAI API connection successful.")
    print("[OK] Models endpoint responded.")
except Exception as e:
    print("[ERROR] API connection failed.")
    print(type(e).__name__, str(e))