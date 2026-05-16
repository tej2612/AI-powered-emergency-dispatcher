"""Test API keys"""

import os
from dotenv import load_dotenv
import google.generativeai as genai
from tavily import TavilyClient

load_dotenv()

print("🧪 Testing API Keys...\n")

# Test GEMINI_API_KEY
print("1️⃣ Testing GEMINI_API_KEY (for web search)...")
gemini_key = os.getenv("GEMINI_API_KEY")
if gemini_key:
    print(f"   Key found: {gemini_key[:20]}...")
    try:
        genai.configure(api_key=gemini_key)
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content("Say hello")
        print(f"   ✅ Success: {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
else:
    print("   ❌ Key not found in .env")

print()

# Test GOOGLE_API_KEY
print("2️⃣ Testing GOOGLE_API_KEY (for dispatcher)...")
google_key = os.getenv("GOOGLE_API_KEY")
if google_key:
    print(f"   Key found: {google_key[:20]}...")
    try:
        genai.configure(api_key=google_key)
        model = genai.GenerativeModel("gemini-2.0-flash-exp")
        response = model.generate_content("Say hello")
        print(f"   ✅ Success: {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
else:
    print("   ❌ Key not found in .env")

print()

# Test TAVILY_API_KEY
print("3️⃣ Testing TAVILY_API_KEY...")
tavily_key = os.getenv("TAVILY_API_KEY")
if tavily_key:
    print(f"   Key found: {tavily_key[:20]}...")
    try:
        client = TavilyClient(api_key=tavily_key)
        result = client.search("test query", max_results=1)
        print(f"   ✅ Success: Found {len(result.get('results', []))} results")
    except Exception as e:
        print(f"   ❌ Error: {e}")
else:
    print("   ❌ Key not found in .env")

print("\n✅ All tests complete!")