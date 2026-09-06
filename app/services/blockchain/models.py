"""
Blockchain module data structures.
"""

from dataclasses import dataclass


@dataclass
class BlockchainRecord:
    """Represents an on-chain evidence registration on Polygon Amoy or local node."""

    tx_hash: str
    block_number: int
    contract_address: str
    network: str
    evidence_hash: str
    metadata_ref: str
    timestamp: int
    explorer_url: str
