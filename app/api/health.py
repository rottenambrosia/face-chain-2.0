"""
Health-check endpoint.
"""

from fastapi import APIRouter

from app.config import settings

router = APIRouter()


@router.get("/health")
async def health():
    """Return service health status and configuration summary."""
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "search_provider": settings.SEARCH_PROVIDER,
        "blockchain_rpc": settings.POLYGON_AMOY_RPC_URL,
        "contract_address": settings.CONTRACT_ADDRESS or "(not deployed yet)",
        "ipfs_enabled": settings.IPFS_ENABLED,
    }
