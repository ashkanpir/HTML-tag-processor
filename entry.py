import openai
import os

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("❌ API key is missing!")

try:
    client = openai.OpenAI(api_key=api_key)  # ✅ Correct OpenAI client usage
    models = client.models.list()
    print("✅ API Connection Successful! Available models:", [model.id for model in models.data])
except openai.OpenAIError as e:
    print(f"❌ OpenAI API Error: {e}")
