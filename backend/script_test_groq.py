"""
Direct Groq API test — reads key from .env file only (ignores env vars)
"""
import os

# Manually read .env to bypass system env vars
env_path = os.path.join(os.path.dirname(__file__), ".env")
env_vars = {}
with open(env_path) as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            env_vars[k.strip()] = v.strip()

api_key = env_vars.get("GROQ_API_KEY", "NOT FOUND")
model   = env_vars.get("GROQ_MODEL", "llama3-8b-8192")

print(f"Key from .env : {api_key[:10]}...{api_key[-6:]}")
print(f"Model         : {model}")
print("-" * 50)

from groq import Groq

try:
    client = Groq(api_key=api_key)
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": "Say hello in one sentence."}],
        max_tokens=30,
    )
    print("✅ Groq API SUCCESS!")
    print("Response:", response.choices[0].message.content)
except Exception as e:
    print(f"❌ Groq API FAILED: {type(e).__name__}: {e}")
