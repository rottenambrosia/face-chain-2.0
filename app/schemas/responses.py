"""
Pydantic response models for the API layer.
"""

from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    app: str
    search_provider: str
    blockchain_rpc: str
    contract_address: str
    ipfs_enabled: bool


class FaceResult(BaseModel):
    detected: bool
    confidence: float
    bbox: list[int]
    aligned_face_path: str


class SearchSelectedCandidate(BaseModel):
    rank: int
    score: int
    source_url: str


class SearchResult(BaseModel):
    provider: str
    candidates_found: int
    selected: SearchSelectedCandidate | None = None


class EvidenceResult(BaseModel):
    hash: str
    canonical_json_path: str
    ipfs_cid: str | None = None


class BlockchainResult(BaseModel):
    tx_hash: str
    block_number: int
    explorer_url: str


class PipelineRunResponse(BaseModel):
    case_id: str
    status: str
    face: FaceResult | None = None
    search: SearchResult | None = None
    evidence: EvidenceResult | None = None
    blockchain: BlockchainResult | None = None


class VerifyResponse(BaseModel):
    case_id: str
    recomputed_hash: str
    on_chain_hash: str
    match: bool
    tamper_detected: bool
    on_chain_timestamp: int
