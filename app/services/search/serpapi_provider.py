"""
SerpApi Google Lens — Genuine Reverse Image Search Provider.

Uses SerpApi's Google Lens engine to perform real reverse face/image search
against the live web.  Returns actual web pages where visually similar images
appear (social media, news, blogs, etc.).

API docs: https://serpapi.com/google-lens-api
Free tier: 100 searches/month, no credit card required.
"""

import base64
import json
import logging
from pathlib import Path
from typing import List

from app.config import settings
from app.services.search.base import SearchProvider
from app.services.search.models import SearchCandidate

logger = logging.getLogger(__name__)


class SerpApiProvider(SearchProvider):
    """Genuine reverse image search via SerpApi Google Lens."""

    def provider_name(self) -> str:
        return "serpapi_google_lens"

    async def search(self, image_path: str, artifact_dir: str) -> List[SearchCandidate]:
        if not settings.SERPAPI_API_KEY:
            raise ValueError(
                "SERPAPI_API_KEY is not configured. "
                "Get a free key at https://serpapi.com (100 searches/month)."
            )

        # Import here so the package is only needed when this provider is used
        from serpapi import GoogleSearch

        logger.info("SerpApi: Starting genuine Google Lens reverse image search for %s", image_path)

        # Read the image and encode as a data URI for the SerpApi `url` param.
        # SerpApi also accepts a public URL — if the image were publicly hosted
        # we could pass the URL directly. For local files we upload via their
        # `url` parameter using a base64 data-URI, OR we can use their file
        # upload approach.  The most reliable method for local images is to use
        # the `image_content` approach via a temporary upload.

        img_path = Path(image_path)
        if not img_path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")

        # SerpApi Google Lens file upload is a two-step process:
        # 1. Upload the image to /image to get an `image_id`
        # 2. Pass `image_id` to Google Lens engine

        import requests as req_lib

        api_key = settings.SERPAPI_API_KEY
        upload_url = "https://serpapi.com/image"

        with open(image_path, "rb") as img_file:
            logger.info("SerpApi: Uploading image to SerpApi image cache...")
            response = req_lib.post(
                upload_url,
                data={"api_key": api_key},
                files={"image": (img_path.name, img_file, "image/jpeg")},
                timeout=120,
            )

        if response.status_code != 200:
            raise RuntimeError(
                f"SerpApi image upload failed (HTTP {response.status_code}): {response.text[:500]}"
            )

        image_id = response.json().get("image_id")
        if not image_id:
            raise RuntimeError(f"SerpApi did not return an image_id: {response.text[:500]}")

        logger.info("SerpApi: Image uploaded successfully, image_id=%s. Running Google Lens search...", image_id)

        params = {
            "engine": "google_lens",
            "api_key": api_key,
            "image_id": image_id,
        }

        search = GoogleSearch(params)
        try:
            result = search.get_dict()
        except Exception as e:
            raise RuntimeError(f"SerpApi Google Lens search failed: {e}")

        # Save raw API response as artifact for full transparency
        raw_path = Path(artifact_dir) / "search_raw_response.json"
        raw_path.parent.mkdir(parents=True, exist_ok=True)
        raw_path.write_text(json.dumps(result, indent=2, default=str))

        # Check for API errors
        if "error" in result:
            raise RuntimeError(f"SerpApi error: {result['error']}")

        # Parse visual matches — these are pages where the image (or similar)
        # was found on the live web
        visual_matches = result.get("visual_matches", [])
        knowledge_graph = result.get("knowledge_graph", [])

        candidates: List[SearchCandidate] = []

        for rank, match in enumerate(visual_matches, 1):
            source_url = match.get("link", "")
            title = match.get("title", "")
            source_name = match.get("source", "")
            thumbnail = match.get("thumbnail", "")
            position = match.get("position", rank)

            if not source_url:
                continue

            candidates.append(
                SearchCandidate(
                    rank=rank,
                    score=max(100 - (rank - 1) * 5, 10),  # Positional score: top result = 100
                    source_url=source_url,
                    thumbnail_b64=thumbnail,
                    provider="serpapi_google_lens",
                    raw_data={
                        "title": title,
                        "url": source_url,
                        "source": source_name,
                        "thumbnail": thumbnail,
                        "position": position,
                        "platform": _guess_platform(source_url),
                    },
                )
            )

        # Also check knowledge graph for social profiles
        for kg_item in knowledge_graph:
            if isinstance(kg_item, dict):
                link = kg_item.get("link", "")
                title = kg_item.get("title", "")
                if link and link not in [c.source_url for c in candidates]:
                    candidates.append(
                        SearchCandidate(
                            rank=len(candidates) + 1,
                            score=max(100 - len(candidates) * 5, 10),
                            source_url=link,
                            thumbnail_b64=kg_item.get("thumbnail", ""),
                            provider="serpapi_google_lens",
                            raw_data={
                                "title": title,
                                "url": link,
                                "source": "knowledge_graph",
                                "platform": _guess_platform(link),
                            },
                        )
                    )

        logger.info(
            "SerpApi: Google Lens returned %d visual matches for %s",
            len(candidates),
            img_path.name,
        )

        return candidates


def _guess_platform(url: str) -> str:
    """Heuristically guess the social platform from a URL."""
    url_lower = url.lower()
    platforms = {
        "twitter.com": "Twitter / X",
        "x.com": "Twitter / X",
        "instagram.com": "Instagram",
        "facebook.com": "Facebook",
        "linkedin.com": "LinkedIn",
        "tiktok.com": "TikTok",
        "youtube.com": "YouTube",
        "reddit.com": "Reddit",
        "pinterest.com": "Pinterest",
        "flickr.com": "Flickr",
        "tumblr.com": "Tumblr",
    }
    for domain, name in platforms.items():
        if domain in url_lower:
            return name
    return "Web"
