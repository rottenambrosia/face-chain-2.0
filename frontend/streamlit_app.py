"""
FaceChain 2.0 — Streamlit Interactive Frontend
Face Scan → Web Search → Blockchain Verification Pipeline
"""

import json
import os
from pathlib import Path
import streamlit as st
import httpx

# ── Page Configuration & Theming ─────────────────────────────────────────────
st.set_page_config(
    page_title="FaceChain 2.0 | Biometric Web3 Provenance",
    page_icon="🔗",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for rich aesthetics and clean typography
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .main-header {
        background: linear-gradient(135deg, #1e1b4b 0%, #312e81 50%, #4338ca 100%);
        border-radius: 12px;
        padding: 24px 32px;
        margin-bottom: 24px;
        color: #ffffff;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
    }
    
    .status-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.82rem;
    }
    .badge-success { background-color: #065f46; color: #34d399; }
    .badge-info { background-color: #1e3a8a; color: #93c5fd; }
    .badge-warn { background-color: #78350f; color: #fde68a; }
    .badge-danger { background-color: #7f1d1d; color: #fca5a5; }

    .metric-card {
        background: rgba(30, 41, 59, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 12px;
    }
    
    .hash-code {
        font-family: monospace;
        background: #0f172a;
        padding: 6px 10px;
        border-radius: 6px;
        border: 1px solid #334155;
        font-size: 0.85rem;
        word-break: break-all;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Backend URL configuration
API_BASE_URL = os.environ.get("API_BASE_URL", "http://127.0.0.1:8000/api/v1")

# ── Sidebar Configuration & Health ───────────────────────────────────────────
with st.sidebar:
    st.image("https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=400&auto=format&fit=crop&q=60&ixlib=rb-4.0.3", caption="FaceChain 2.0 Engine")
    st.markdown("### ⚙️ System Status")
    
    try:
        resp = httpx.get("http://127.0.0.1:8000/api/v1/health", timeout=3.0)
        if resp.status_code == 200:
            health = resp.json()
            st.markdown(f"**Backend:** <span class='status-badge badge-success'>ONLINE</span>", unsafe_allow_html=True)
            st.markdown(f"**Network:** `{health.get('blockchain_rpc', 'Polygon Amoy')}`")
            st.markdown(f"**Search Engine:** `{health.get('search_provider', 'facecheck')}`")
        else:
            st.markdown(f"**Backend:** <span class='status-badge badge-warn'>STANDBY</span>", unsafe_allow_html=True)
    except Exception:
        st.markdown(f"**Backend:** <span class='status-badge badge-info'>STANDALONE / DIRECT</span>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 🛡️ Privacy Principles")
    st.caption(
        "• **Zero Biometrics On-Chain:** Face embeddings & photos never leave the secure server.\n"
        "• **Tamper-Evident:** Only cryptographic SHA-256 hashes are recorded on Polygon Amoy.\n"
        "• **Public Verifiability:** Anyone can audit digital provenance with a single click."
    )

# ── Header ───────────────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="main-header">
        <h1 style="margin:0; font-size:2rem; font-weight:700;">🔗 FaceChain 2.0</h1>
        <p style="margin: 6px 0 0 0; opacity: 0.85; font-size: 1.05rem;">
            End-to-End Face Scan → Web Reverse Search → Blockchain Verification Pipeline
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

tab1, tab2, tab3 = st.tabs(["🚀 Run Pipeline", "🔍 Verify & Tamper Test", "📐 Architecture & Security"])

# ── Tab 1: Run Pipeline ───────────────────────────────────────────────────────
with tab1:
    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.subheader("1. Upload Face Scan")
        uploaded_file = st.file_uploader(
            "Choose a clear face image (JPEG or PNG)",
            type=["jpg", "jpeg", "png"],
            help="Images are processed strictly for detection, aligned crop, and reverse search.",
        )

        auto_select = st.checkbox("Auto-select highest scoring social candidate", value=True)

        if uploaded_file is not None:
            st.image(uploaded_file, caption="Input Scan Preview", use_container_width=True)

        run_button = st.button("⚡ Run End-to-End Pipeline", type="primary", disabled=(uploaded_file is None), use_container_width=True)

    with col_right:
        st.subheader("2. Live Pipeline Execution")

        if run_button and uploaded_file is not None:
            status_placeholder = st.empty()
            progress_bar = st.progress(0)

            status_placeholder.info("⏳ Step 1/4: Analyzing face scan & extracting embeddings...")
            progress_bar.progress(25)

            try:
                # Direct API invocation or internal execution
                files = {"images": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                params = {"auto_select": auto_select}

                status_placeholder.info("🌐 Step 2/4: Searching web & social platforms for matching posts...")
                progress_bar.progress(50)

                with httpx.Client(timeout=180.0) as client:
                    response = client.post(f"{API_BASE_URL}/pipeline/run", files=files, params=params)

                progress_bar.progress(85)
                status_placeholder.info("⛓️ Step 3 & 4: Hashing canonical evidence & anchoring to Polygon Amoy...")

                if response.status_code == 200:
                    data = response.json()
                    progress_bar.progress(100)
                    status_placeholder.success("✅ End-to-End Pipeline Completed Successfully!")

                    st.session_state["last_case_id"] = data["case_id"]
                    st.session_state["last_run_data"] = data

                else:
                    status_placeholder.error(f"❌ Pipeline failed: {response.text}")
            except Exception as e:
                status_placeholder.error(f"❌ Communication error: {e}")

        # Render Results if available in session
        if "last_run_data" in st.session_state:
            res = st.session_state["last_run_data"]
            st.markdown(f"### 📋 Case: `{res['case_id']}`")
            
            # Step 1: Face
            with st.expander("👤 Step 1: Face Detection & Biometric Extraction", expanded=True):
                f_col1, f_col2 = st.columns([1, 2])
                with f_col1:
                    st.metric("Confidence", f"{res['face']['confidence']*100:.1f}%")
                    st.caption(f"Bounding Box: `{res['face']['bbox']}`")
                with f_col2:
                    st.success("Face successfully detected & 512-d ArcFace vector extracted.")
                    st.caption("Biometric vector kept confidential; not uploaded on-chain.")

            # Step 2: Search Match
            with st.expander("🌐 Step 2: Social Media & Web Match Discovered", expanded=True):
                if res["search"] and res["search"]["selected"]:
                    sel = res["search"]["selected"]
                    provider_name = res["search"].get("provider", "unknown")
                    is_live = provider_name != "mock"
                    
                    if is_live:
                        st.markdown(
                            "<span class='status-badge badge-success'>🔴 LIVE SEARCH</span> "
                            f"<span style='opacity:0.7;font-size:0.85rem;'>via {provider_name}</span>",
                            unsafe_allow_html=True,
                        )
                    else:
                        st.markdown(
                            "<span class='status-badge badge-warn'>⚠️ DEMO MODE</span> "
                            "<span style='opacity:0.7;font-size:0.85rem;'>Mock data — set SERPAPI_API_KEY for real search</span>",
                            unsafe_allow_html=True,
                        )
                    
                    st.markdown(f"**Found On:** [{sel['source_url']}]({sel['source_url']})")
                    s_col1, s_col2 = st.columns(2)
                    with s_col1:
                        st.metric("Match Score", f"{sel['score']}/100")
                    with s_col2:
                        st.metric("Candidates Evaluated", res["search"]["candidates_found"])
                    
                    # Show all candidates with details
                    all_cands = res["search"].get("all_candidates", [])
                    if all_cands and is_live:
                        st.markdown("**All Discovered Matches:**")
                        for c in all_cands[:5]:
                            raw = c.get("raw_data", {})
                            title = raw.get("title", "Untitled")
                            platform = raw.get("platform", "Web")
                            url = c.get("source_url", "")
                            thumb = raw.get("thumbnail", "")
                            
                            cols = st.columns([1, 4]) if thumb else [st.container()]
                            if thumb:
                                with cols[0]:
                                    st.image(thumb, width=80)
                                with cols[1]:
                                    st.markdown(f"**{title}** ({platform})")
                                    st.caption(f"[{url}]({url}) — Score: {c.get('score', '?')}/100")
                            else:
                                st.markdown(f"- **{title}** ({platform}) — [{url}]({url}) — Score: {c.get('score', '?')}/100")
                else:
                    st.warning("No high-confidence matches found on the web.")

            # Step 3: Evidence Hash
            with st.expander("🔒 Step 3: Canonical Evidence & Cryptographic Hash", expanded=True):
                ev = res["evidence"]
                st.markdown("**Deterministic SHA-256 Fingerprint:**")
                st.markdown(f"<div class='hash-code'>{ev['hash']}</div>", unsafe_allow_html=True)
                if ev.get("ipfs_cid"):
                    st.caption(f"IPFS CID: `{ev['ipfs_cid']}`")

            # Step 4: Blockchain Anchor
            with st.expander("⛓️ Step 4: Polygon Amoy Smart Contract Anchor", expanded=True):
                bc = res["blockchain"]
                st.markdown(f"**Transaction Hash:**")
                st.markdown(f"<div class='hash-code'>{bc['tx_hash']}</div>", unsafe_allow_html=True)
                st.markdown(f"**Block Number:** `{bc['block_number']}` | **Network:** `{bc['network']}`")
                st.markdown(f"🔗 **[View on Polygonscan Explorer]({bc['explorer_url']})**")

# ── Tab 2: Re-Verify & Tamper Test ────────────────────────────────────────────
with tab2:
    st.subheader("Cryptographic Re-Verification & Tamper Detection")
    st.markdown(
        "Verify that local evidence has not been modified or corrupted by comparing its recomputed "
        "SHA-256 fingerprint with the immutable record anchored on the blockchain."
    )

    verify_case_id = st.text_input(
        "Enter Case ID to verify",
        value=st.session_state.get("last_case_id", ""),
        placeholder="e.g. fc_20260906_a1b2c3",
    )

    v_col1, v_col2 = st.columns(2)

    with v_col1:
        if st.button("🛡️ Verify Against Blockchain", type="primary", use_container_width=True):
            if not verify_case_id:
                st.warning("Please enter a valid Case ID.")
            else:
                with st.spinner("Querying blockchain and recomputing local hash..."):
                    try:
                        with httpx.Client(timeout=30.0) as client:
                            resp = client.post(
                                f"{API_BASE_URL}/pipeline/verify",
                                json={"case_id": verify_case_id},
                            )
                        if resp.status_code == 200:
                            v_data = resp.json()
                            if v_data["match"]:
                                st.success("✅ **VERIFICATION SUCCESSFUL: Hashes Match Exactly!**")
                                st.markdown(f"**Recomputed SHA-256:**\n`<span class='hash-code'>{v_data['recomputed_hash']}</span>`", unsafe_allow_html=True)
                                st.markdown(f"**On-Chain Record:**\n`<span class='hash-code'>{v_data['on_chain_hash']}</span>`", unsafe_allow_html=True)
                                st.caption(f"Anchored at timestamp: {v_data['on_chain_timestamp']}")
                            else:
                                st.error("🚨 **TAMPER DETECTED: Hashes do not match!**")
                        else:
                            st.error(f"Verification request failed: {resp.text}")
                    except Exception as e:
                        st.error(f"Error connecting to backend: {e}")

    with v_col2:
        st.markdown("**🔬 Tamper Demonstration Tool**")
        st.caption("Alter one byte in the local evidence file to demonstrate cryptographic tamper-detection to judges:")
        
        if st.button("⚠️ Simulate Evidence Tampering", type="secondary", use_container_width=True):
            if not verify_case_id:
                st.warning("Please enter a valid Case ID first.")
            else:
                evidence_file = Path("data/artifacts") / verify_case_id / "evidence.json"
                if evidence_file.exists():
                    with open(evidence_file, "r", encoding="utf-8") as f:
                        content = f.read()
                    tampered = content.replace("2.0.0", "2.0.1-TAMPERED")
                    with open(evidence_file, "w", encoding="utf-8") as f:
                        f.write(tampered)
                    st.warning(f"Tampered with {evidence_file.name}! Now click 'Verify Against Blockchain' to see tamper detection.")
                else:
                    st.error("Evidence file not found on disk.")

# ── Tab 3: Architecture & Security ────────────────────────────────────────────
with tab3:
    st.subheader("System Architecture & Security Model")
    st.markdown(
        """
        ```
        User Input Image 
              │
              ▼
        [1. Face Processing]
           • Model: InsightFace (ArcFace + RetinaFace)
           • Output: 112×112 Aligned Face + 512-d normalized embedding
           • Artifacts: Stored securely server-side; NEVER sent to blockchain
              │
              ▼
        [2. Reverse Web/Social Search]
           • Provider: FaceCheck.id API (live web reverse face search)
           • Fallback: MockSearchProvider (deterministic cached demo records)
           • Result: Matched social media URL, match score (0-100), author metadata
              │
              ▼
        [3. Evidence Canonicalization & Hashing]
           • Format: Deterministic canonical JSON (RFC 8785 conventions)
           • Hash: SHA-256 cryptographic digest
           • Storage: Off-chain canonical JSON + optional Pinata IPFS
              │
              ▼
        [4. Smart Contract Anchoring]
           • Contract: EvidenceRegistry.sol
           • Network: Polygon Amoy (Chain ID 80002)
           • Storage: Mapping(caseId => Evidence(hash, metadataRef, submitter, timestamp))
        ```
        """
    )

    st.markdown("### Why Polygon Amoy Testnet?")
    st.markdown(
        "- **Speed:** ~2-second block finality allows fast end-to-end demo execution.\n"
        "- **Public Verifiability:** Every transaction is immediately visible on Polygonscan.\n"
        "- **EVM Standard:** Production-compatible with Ethereum mainnet, Arbitrum, and Polygon PoS."
    )
