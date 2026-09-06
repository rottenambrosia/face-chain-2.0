"""
Face detection data structures.
"""

from dataclasses import dataclass
from typing import List, Optional
import numpy as np


@dataclass
class FaceDetectionResult:
    """Result of detecting, cropping, and embedding a face from an image."""

    detected: bool
    bbox: List[int]  # [x1, y1, x2, y2]
    confidence: float  # 0.0 - 1.0
    aligned_face_path: str  # Path to saved cropped / aligned face
    embedding: Optional[np.ndarray] = None  # 512-d normalized vector
    embedding_path: Optional[str] = None  # Path to saved .npy file
