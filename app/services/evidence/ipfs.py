"""
Pinata IPFS client for off-chain evidence persistence.
"""

import logging
from typing import Dict, Any, Optional
import httpx

from app.config import settings

logger = logging.getLogger(__name__)


class IPFSClient:
    """Optional IPFS client using Pinata REST API."""

    @staticmethod
    async def pin_json(canonical_json: Dict[str, Any], name: str) -> Optional[str]:
        """Pin canonical evidence dictionary to Pinata IPFS. Returns CID hash."""
        if not settings.IPFS_ENABLED or not settings.PINATA_JWT:
            logger.info("IPFS pinning is disabled or PINATA_JWT is not set.")
            return None

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(
                    "https://api.pinata.cloud/pinning/pinJSONToIPFS",
                    headers={
                        "Authorization": f"Bearer {settings.PINATA_JWT}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "pinataContent": canonical_json,
                        "pinataMetadata": {"name": name},
                    },
                )
                resp.raise_for_status()
                cid = resp.json().get("IpfsHash")
                logger.info("Pinned evidence to IPFS: %s", cid)
                return cid
        except Exception as e:
            logger.warning("IPFS pinning failed: %s. Continuing without IPFS.", e)
            return None
