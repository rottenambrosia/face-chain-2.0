require("dotenv").config({ path: "../.env" });
require("@nomicfoundation/hardhat-toolbox");

const accounts = process.env.DEPLOYER_PRIVATE_KEY
  ? [process.env.DEPLOYER_PRIVATE_KEY.startsWith("0x") ? process.env.DEPLOYER_PRIVATE_KEY : `0x${process.env.DEPLOYER_PRIVATE_KEY}`]
  : [];

module.exports = {
  solidity: "0.8.24",
  networks: {
    polygon_amoy: {
      url: process.env.POLYGON_AMOY_RPC_URL || "https://rpc-amoy.polygon.technology/",
      accounts: accounts.length > 0 ? accounts : undefined,
      chainId: 80002,
    },
    localhost: {
      url: "http://127.0.0.1:8545",
    },
  },
  etherscan: {
    apiKey: {
      polygonAmoy: process.env.POLYGONSCAN_API_KEY || "",
    },
  },
};
