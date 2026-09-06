"""
Blockchain client for anchoring and verifying evidence on Polygon Amoy or local EVM chain.
"""

import hashlib
import json
import logging
import time
from pathlib import Path
from typing import Dict, Any, Optional
from web3 import Web3

from app.config import settings
from app.services.blockchain.models import BlockchainRecord

logger = logging.getLogger(__name__)


class BlockchainClient:
    """Interacts with EvidenceRegistry smart contract via Web3.py."""

    def __init__(self):
        self.w3: Optional[Web3] = None
        self.contract = None
        self.account = None
        self.is_connected = False
        self._mock_chain: Dict[str, Dict[str, Any]] = {}
        self._init_web3()

    def _init_web3(self):
        try:
            self.w3 = Web3(Web3.HTTPProvider(settings.POLYGON_AMOY_RPC_URL))
            try:
                from web3.middleware import ExtraDataToPOAMiddleware
                self.w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)
            except Exception:
                try:
                    from web3.middleware import geth_poa_middleware
                    self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
                except Exception:
                    pass

            # Load ABI
            abi_path = Path(__file__).parent / "abi" / "EvidenceRegistry.json"
            if abi_path.exists():
                with open(abi_path, "r", encoding="utf-8") as f:
                    contract_data = json.load(f)
                abi = contract_data["abi"] if isinstance(contract_data, dict) and "abi" in contract_data else contract_data
            else:
                abi = []

            # Check if private key and contract address are available
            if settings.CONTRACT_ADDRESS and Web3.is_address(settings.CONTRACT_ADDRESS):
                self.contract = self.w3.eth.contract(
                    address=Web3.to_checksum_address(settings.CONTRACT_ADDRESS),
                    abi=abi,
                )

            if settings.DEPLOYER_PRIVATE_KEY:
                pk = settings.DEPLOYER_PRIVATE_KEY
                if not pk.startswith("0x"):
                    pk = "0x" + pk
                self.account = self.w3.eth.account.from_key(pk)

            self.is_connected = self.w3.is_connected()
            logger.info("Web3 initialized. Connected to RPC: %s", self.is_connected)
        except Exception as e:
            logger.warning("Could not initialize live Web3 connection (%s). Local fallback active.", e)
            self.is_connected = False

    def store_evidence(self, case_id: str, evidence_hash: str, metadata_ref: str) -> BlockchainRecord:
        """Store evidence hash on-chain (or simulated ledger if offline)."""
        clean_hash = evidence_hash.lower()
        if not clean_hash.startswith("0x"):
            clean_hash = "0x" + clean_hash

        # If live contract and account are ready, send on-chain tx
        if self.is_connected and self.contract and self.account:
            try:
                hash_bytes = bytes.fromhex(clean_hash.replace("0x", ""))
                nonce = self.w3.eth.get_transaction_count(self.account.address)
                tx = self.contract.functions.storeEvidence(
                    case_id,
                    hash_bytes,
                    metadata_ref,
                ).build_transaction({
                    "from": self.account.address,
                    "nonce": nonce,
                    "gas": 200000,
                    "gasPrice": self.w3.to_wei("30", "gwei"),
                })
                signed = self.w3.eth.account.sign_transaction(tx, self.account.key)
                tx_hash_bytes = self.w3.eth.send_raw_transaction(signed.raw_transaction)
                receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash_bytes, timeout=60)
                tx_hash_hex = receipt.transactionHash.hex()
                if not tx_hash_hex.startswith("0x"):
                    tx_hash_hex = "0x" + tx_hash_hex

                block = self.w3.eth.get_block(receipt.blockNumber)
                timestamp = block.timestamp

                return BlockchainRecord(
                    tx_hash=tx_hash_hex,
                    block_number=receipt.blockNumber,
                    contract_address=settings.CONTRACT_ADDRESS,
                    network="polygon_amoy",
                    evidence_hash=clean_hash,
                    metadata_ref=metadata_ref,
                    timestamp=timestamp,
                    explorer_url=f"https://amoy.polygonscan.com/tx/{tx_hash_hex}",
                )
            except Exception as e:
                logger.warning("On-chain transaction failed (%s). Falling back to simulated ledger.", e)

        # Simulated fallback ledger for seamless demo/testing
        now_ts = int(time.time())
        simulated_tx = "0x" + hashlib.sha256(f"{case_id}{clean_hash}{now_ts}".encode("utf-8")).hexdigest()
        self._mock_chain[case_id] = {
            "evidence_hash": clean_hash,
            "metadata_ref": metadata_ref,
            "submitter": self.account.address if self.account else "0x71C8366453AB548A392d45672951234F315E4912",
            "timestamp": now_ts,
            "block_number": 14285700,
            "tx_hash": simulated_tx,
        }

        return BlockchainRecord(
            tx_hash=simulated_tx,
            block_number=14285700,
            contract_address=settings.CONTRACT_ADDRESS or "0xEvidenceRegistrySimulatedAddressAmoy",
            network="polygon_amoy (simulated)",
            evidence_hash=clean_hash,
            metadata_ref=metadata_ref,
            timestamp=now_ts,
            explorer_url=f"https://amoy.polygonscan.com/tx/{simulated_tx}",
        )

    def get_evidence(self, case_id: str) -> Dict[str, Any]:
        """Query evidence record from contract or fallback ledger."""
        if self.is_connected and self.contract:
            try:
                result = self.contract.functions.getEvidence(case_id).call()
                ev_hash = "0x" + result[0].hex()
                return {
                    "evidence_hash": ev_hash,
                    "metadata_ref": result[1],
                    "submitter": result[2],
                    "timestamp": result[3],
                }
            except Exception as e:
                logger.warning("Contract getEvidence call failed (%s). Checking fallback ledger.", e)

        if case_id in self._mock_chain:
            return self._mock_chain[case_id]

        raise ValueError(f"No on-chain evidence found for case ID: {case_id}")

    def verify_evidence(self, case_id: str, claimed_hash: str) -> bool:
        """Verify claimed evidence hash against on-chain record."""
        clean_claimed = claimed_hash.lower()
        if not clean_claimed.startswith("0x"):
            clean_claimed = "0x" + clean_claimed

        if self.is_connected and self.contract:
            try:
                hash_bytes = bytes.fromhex(clean_claimed.replace("0x", ""))
                return self.contract.functions.verifyEvidence(case_id, hash_bytes).call()
            except Exception as e:
                logger.warning("Contract verifyEvidence call failed (%s). Checking fallback ledger.", e)

        record = self.get_evidence(case_id)
        return record["evidence_hash"].lower() == clean_claimed
