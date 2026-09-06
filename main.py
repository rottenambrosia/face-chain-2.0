"""
FaceChain 2.0 entrypoint.
Runs the FastAPI server when executed directly: python main.py
"""

import uvicorn
from app.config import settings

if __name__ == "__main__":
    print(f"Starting {settings.APP_NAME} backend server...")
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=settings.DEBUG)
