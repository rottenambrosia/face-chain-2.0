// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/**
 * @title EvidenceRegistry
 * @dev Stores tamper-evident SHA-256 evidence hashes and metadata references for FaceChain cases.
 */
contract EvidenceRegistry {
    struct Evidence {
        bytes32 evidenceHash;     // SHA-256 hash of canonical evidence JSON
        string metadataRef;       // IPFS CID or off-chain case reference
        address submitter;        // Address that registered the evidence
        uint256 timestamp;        // Block timestamp when stored
        bool exists;              // Guard against uninitialized lookups
    }

    // caseId => Evidence
    mapping(string => Evidence) private evidenceRecords;

    // Event emitted when evidence is anchored on-chain
    event EvidenceStored(
        string indexed caseId,
        bytes32 evidenceHash,
        string metadataRef,
        address indexed submitter,
        uint256 timestamp
    );

    /**
     * @notice Store evidence hash for a case. One case = one immutable record.
     * @param caseId Unique identifier of the case
     * @param evidenceHash SHA-256 hash of the canonical evidence JSON
     * @param metadataRef Pointer to off-chain bundle (e.g. IPFS CID or caseId)
     */
    function storeEvidence(
        string calldata caseId,
        bytes32 evidenceHash,
        string calldata metadataRef
    ) external {
        require(!evidenceRecords[caseId].exists, "Evidence already stored for this case");
        require(evidenceHash != bytes32(0), "Evidence hash cannot be zero");

        evidenceRecords[caseId] = Evidence({
            evidenceHash: evidenceHash,
            metadataRef: metadataRef,
            submitter: msg.sender,
            timestamp: block.timestamp,
            exists: true
        });

        emit EvidenceStored(caseId, evidenceHash, metadataRef, msg.sender, block.timestamp);
    }

    /**
     * @notice Retrieve stored evidence for verification.
     * @param caseId Unique identifier of the case
     */
    function getEvidence(string calldata caseId)
        external
        view
        returns (
            bytes32 evidenceHash,
            string memory metadataRef,
            address submitter,
            uint256 timestamp
        )
    {
        Evidence storage record = evidenceRecords[caseId];
        require(record.exists, "No evidence found for this case");
        return (record.evidenceHash, record.metadataRef, record.submitter, record.timestamp);
    }

    /**
     * @notice Verify whether a claimed evidence hash matches the stored on-chain record.
     * @param caseId Unique identifier of the case
     * @param claimedHash SHA-256 hash to compare against on-chain record
     */
    function verifyEvidence(string calldata caseId, bytes32 claimedHash)
        external
        view
        returns (bool)
    {
        Evidence storage record = evidenceRecords[caseId];
        require(record.exists, "No evidence found for this case");
        return record.evidenceHash == claimedHash;
    }
}
