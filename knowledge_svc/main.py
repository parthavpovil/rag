import os
from dotenv import load_dotenv

# Load environment variables from .env file in parent directory
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
print(f"Loading .env from: {env_path}")
load_dotenv(env_path)

# Debug: Print loaded keys
required_vars = ["SUPABASE_URL", "SUPABASE_SERVICE_KEY", "AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY"]
print("Environment Variable Check:")
for var in required_vars:
    value = os.getenv(var)
    print(f"  {var}: {'✅ Set' if value else '❌ Missing'}")

from fastapi import FastAPI
from api.routes import router

app = FastAPI(title="Knowledge Service", version="0.1.0")

app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
