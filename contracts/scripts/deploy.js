const hre = require("hardhat");

async function main() {
  console.log(`Starting deployment of EvidenceRegistry to ${hre.network.name}...`);
  const EvidenceRegistry = await hre.ethers.getContractFactory("EvidenceRegistry");
  const registry = await EvidenceRegistry.deploy();
  await registry.waitForDeployment();

  const address = await registry.getAddress();
  console.log(`✅ EvidenceRegistry deployed successfully!`);
  console.log(`Contract Address: ${address}`);
  console.log(`Network: ${hre.network.name}`);
  console.log(`\nNext step: update CONTRACT_ADDRESS=${address} in your .env file.`);
}

main().catch((error) => {
  console.error("Deployment failed:", error);
  process.exitCode = 1;
});
