"""
FaceCheck.id API Search Provider.
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import List
import httpx

from app.config import settings
from app.services.search.base import SearchProvider
from app.services.search.models import SearchCandidate

logger = logging.getLogger(__name__)


class FaceCheckProvider(SearchProvider):
    """Integrates with FaceCheck.id reverse face search API."""

    SITE = "https://facecheck.id"

    def provider_name(self) -> str:
        return "facecheck"

    async def search(self, image_path: str, artifact_dir: str) -> List[SearchCandidate]:
        if not settings.FACECHECK_API_TOKEN:
            logger.warning("No FACECHECK_API_TOKEN set. Cannot run live FaceCheck search.")
            raise ValueError("FACECHECK_API_TOKEN is not configured in environment.")

        async with httpx.AsyncClient(timeout=120.0) as client:
            headers = {
                "accept": "application/json",
                "Authorization": settings.FACECHECK_API_TOKEN,
            }

            # Step 1: Upload image
            logger.info("Uploading image to FaceCheck: %s", image_path)
            with open(image_path, "rb") as f:
                files = {"images": (Path(image_path).name, f, "image/jpeg")}
                data = {"id_search": ""}
                resp = await client.post(
                    f"{self.SITE}/api/upload_pic",
                    headers=headers,
                    files=files,
                    data=data,
                )

            upload_result = resp.json()
            if upload_result.get("error"):
                raise RuntimeError(
                    f"FaceCheck upload error: {upload_result['error']} (code {upload_result.get('code')})"
                )

            id_search = upload_result.get("id_search")
            if not id_search:
                raise RuntimeError(f"FaceCheck upload failed to return id_search: {upload_result}")

            logger.info("FaceCheck upload OK: id_search=%s", id_search)

            # Step 2: Poll for results
            search_payload = {
                "id_search": id_search,
                "with_progress": True,
                "status_only": False,
                "demo": settings.FACECHECK_TESTING_MODE,
            }

            max_polls = 120  # up to 6 minutes with 3s intervals
            for i in range(max_polls):
                resp = await client.post(
                    f"{self.SITE}/api/search",
                    headers=headers,
                    json=search_payload,
                )
                result = resp.json()

                if result.get("error"):
                    raise RuntimeError(f"FaceCheck search error: {result['error']}")

                if result.get("output"):
                    # Save raw response
                    raw_path = Path(artifact_dir) / "search_raw_response.json"
                    raw_path.parent.mkdir(parents=True, exist_ok=True)
                    raw_path.write_text(json.dumps(result, indent=2))

                    items = result["output"].get("items", [])
                    candidates = []
                    for rank, item in enumerate(items, 1):
                        candidates.append(
                            SearchCandidate(
                                rank=rank,
                                score=item.get("score", 0),
                                source_url=item.get("url", ""),
                                thumbnail_b64=item.get("base64", ""),
                                provider="facecheck",
                                raw_data=item,
                            )
                        )

                    candidates.sort(key=lambda c: c.score, reverse=True)
                    for idx, c in enumerate(candidates, 1):
                        c.rank = idx

                    logger.info("FaceCheck returned %d candidates", len(candidates))
                    return candidates

                progress = result.get("progress", 0)
                logger.info("FaceCheck searching in progress... %s%%", progress)
                await asyncio.sleep(3)

            raise TimeoutError("FaceCheck search timed out waiting for results")
