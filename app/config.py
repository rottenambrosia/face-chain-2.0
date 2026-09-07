"""
Application configuration — loads all settings from environment variables / .env file.
"""

from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Central configuration loaded from .env via pydantic-settings."""

    # ── Application ──────────────────────────────────────────────────────
    APP_NAME: str = "FaceChain 2.0"
    DEBUG: bool = False

    # ── Paths ────────────────────────────────────────────────────────────
    DATA_DIR: Path = Path("data")
    UPLOADS_DIR: Path = Path("data/uploads")
    ARTIFACTS_DIR: Path = Path("data/artifacts")

    # ── Face Detection ───────────────────────────────────────────────────
    INSIGHTFACE_MODEL: str = "buffalo_l"
    MIN_FACE_CONFIDENCE: float = 0.5

    # ── Search ───────────────────────────────────────────────────────────
    SEARCH_PROVIDER: str = "serpapi"  # "serpapi" | "facecheck" | "mock"
    SERPAPI_API_KEY: str = ""
    FACECHECK_API_TOKEN: str = ""
    FACECHECK_TESTING_MODE: bool = True
    AUTO_SELECT_THRESHOLD: int = 70

    # ── Blockchain (Polygon Amoy) ────────────────────────────────────────
    POLYGON_AMOY_RPC_URL: str = "https://rpc-amoy.polygon.technology/"
    DEPLOYER_PRIVATE_KEY: str = ""
    CONTRACT_ADDRESS: str = ""

    # ── IPFS / Pinata (optional) ─────────────────────────────────────────
    PINATA_JWT: str = ""
    IPFS_ENABLED: bool = False

    # ── Database ─────────────────────────────────────────────────────────
    DATABASE_URL: str = "sqlite:///./data/facechain.db"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
