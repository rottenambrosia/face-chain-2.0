# 🔗 FaceChain 2.0

> **End-to-End Face Scan → Web Reverse Search → Blockchain Verification Pipeline**

FaceChain 2.0 detects and encodes a face from an input scan, discovers matching social media posts across the web, builds an immutable cryptographic evidence bundle, and anchors a tamper-evident record onto the **Polygon Amoy** blockchain.

---

## 🚀 Key Highlights & Architectural Pillars

1. **Genuine Reverse Face Search**: Integrates with the FaceCheck.id API for live cross-web face discovery across social media (Twitter/X, LinkedIn, Instagram, etc.), with automatic fallback to high-fidelity mock data for offline demos.
2. **Zero Biometrics On-Chain (Privacy-by-Design)**: Facial embeddings (512-d vectors) and raw biometrics stay strictly off-chain on secure local servers. Only deterministic SHA-256 fingerprints of canonical evidence are committed to smart contracts.
3. **Deterministic Canonical Hashing**: Generates RFC-compliant canonical JSON (sorted keys, compact delimiters) and SHA-256 digests ensuring identical bit-level reproducibility on any machine.
4. **Instant Tamper Detection & Re-Verification**: Provides a one-click re-verification mechanism that queries Polygon Amoy and recomputes the local hash. Modifying even a single character in the local evidence immediately triggers a tamper alert.
5. **Modern Dual-Layer Interface**: Features both an interactive **Streamlit Dashboard** and a high-performance **FastAPI REST API** with OpenAPI interactive documentation.

---

## 📐 System Architecture

```
User uploads Face Scan (JPEG / PNG)
               │
               ▼
┌─────────────────────────────────────────────────────────────┐
│ [1] Face Detection & Embedding                              │
│  • RetinaFace & ArcFace / OpenCV Fallback                   │
│  • Crops & aligns face with 20% margin                      │
│  • Extracts normalized 512-d biometric embedding            │
│  • Saves aligned face crop & embedding locally              │
└──────────────────────────────┬──────────────────────────────┘
                               │ Aligned Face Crop
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ [2] Web / Social Media Reverse Search                       │
│  • FaceCheck.id REST API (Upload → Poll → Normalize)        │
│  • Fallback: MockSearchProvider for offline demo safety     │
│  • Returns candidate URLs, match confidence scores & thumbs │
└──────────────────────────────┬──────────────────────────────┘
                               │ Top Matched Candidate URL + Score
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ [3] Evidence Canonicalization & Hashing                     │
│  • Builds deterministic canonical dictionary                │
│  • Computes SHA-256 hash (0x + 64 hex characters)           │
│  • Optional Pinata IPFS pinning for decentralized metadata  │
└──────────────────────────────┬──────────────────────────────┘
                               │ SHA-256 Evidence Hash
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ [4] Blockchain Anchoring (Polygon Amoy)                     │
│  • Smart Contract: EvidenceRegistry.sol                     │
│  • Calls storeEvidence(caseId, evidenceHash, metadataRef)   │
│  • Emits EvidenceStored event and returns transaction hash  │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ [5] Cryptographic Re-Verification                           │
│  • Recomputes local SHA-256 from evidence.json              │
│  • Compares with on-chain record via getEvidence(caseId)    │
│  • Verdict: ✅ MATCH (Verified) or 🚨 MISMATCH (Tampered)    │
└─────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Technology Stack

| Layer | Technology | Rationale |
|---|---|---|
| **Backend API** | FastAPI + Uvicorn | Async Python, automatic OpenAPI docs, typed Pydantic models |
| **Face Engine** | InsightFace (ArcFace) + OpenCV | SOTA facial landmark alignment and 512-d normalized embeddings |
| **Search Engine** | FaceCheck.id API | Specialized facial reverse-image search returning direct post URLs |
| **Blockchain** | Solidity 0.8.24 + Polygon Amoy | 2-second block finality, EVM compatibility, public block explorer |
| **Contract Tooling** | Hardhat | Compilation, testing, deployment scripts |
| **Web3 Client** | Web3.py | On-chain contract interaction, transaction signing, PoA middleware |
| **Frontend UI** | Streamlit | Clean, modern interactive interface with live tamper demonstration |
| **Database** | SQLite + SQLAlchemy | Zero-configuration persistence for case records |

---

## ⚙️ Quickstart & Installation

### 1. Prerequisites
- **Python 3.10+** (Python 3.12 recommended)
- **Node.js 18+** (for Hardhat contract deployment)

### 2. Clone and Setup Environment

```bash
cd d:/FaceChain2.0

# Activate virtual environment
.\.venv\Scripts\activate      # Windows
# or: source .venv/bin/activate # Linux/macOS

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Key configuration parameters:
- `SEARCH_PROVIDER`: Set to `"facecheck"` for live web search or `"mock"` for offline demos.
- `FACECHECK_API_TOKEN`: Your FaceCheck.id API token.
- `FACECHECK_TESTING_MODE`: `true` for testing/dev, `false` for live production searches.
- `POLYGON_AMOY_RPC_URL`: Polygon Amoy RPC endpoint (default: `https://rpc-amoy.polygon.technology/`).
- `DEPLOYER_PRIVATE_KEY`: Wallet private key for Polygon Amoy gas fees.
- `CONTRACT_ADDRESS`: Address of deployed `EvidenceRegistry` contract.

---

## 🚀 Running the Application

### Option A: One-Command Launch (PowerShell)
```powershell
.\run.ps1
```

### Option B: Manual Launch
1. **Start FastAPI Backend**:
   ```bash
   uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
   ```
2. **Start Streamlit Dashboard**:
   ```bash
   streamlit run frontend/streamlit_app.py --server.port 8501
   ```

- **Streamlit UI**: [http://localhost:8501](http://localhost:8501)
- **FastAPI OpenAPI Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Health Check Endpoint**: [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)

---

## 📜 Smart Contract Deployment (Polygon Amoy)

The `EvidenceRegistry.sol` contract is located in `contracts/`.

```bash
cd contracts
npm install
npx hardhat compile

# Deploy to Polygon Amoy
npx hardhat run scripts/deploy.js --network polygon_amoy
```
After deployment, copy the logged address into your `.env` as `CONTRACT_ADDRESS`.

---

## 🧪 Testing & Verification

Run the automated test suite:
```bash
pytest tests -v
```

### Interactive Tamper Demonstration
1. In the Streamlit UI, run a pipeline case under **Run Pipeline**.
2. Switch to **Verify & Tamper Test**. Click **Verify Against Blockchain** to confirm match.
3. Click **Simulate Evidence Tampering** (modifies 1 byte in `evidence.json`).
4. Re-click **Verify Against Blockchain** — notice the immediate `🚨 TAMPER DETECTED` alert!

---

## 🔒 Security & Privacy Commitments

- **No Biometrics On-Chain**: Neither the facial image nor the 512-d mathematical embedding is ever broadcast to the public blockchain or IPFS.
- **Minimization**: Only non-biometric metadata (Case ID, verified URL, match confidence, timestamp) is included in the canonical hash.
- **Immutability**: Once an evidence hash is registered on Polygon Amoy for a given Case ID, the contract rejects any subsequent overwrite attempts.

---

## 📄 License
MIT License. Built for research, digital provenance, and hackathon evaluation.
