// Mock Irys SDK for testing purposes
// import { Irys } from "@irys/sdk";

let irys = null;

export async function getIrys() {
  if (!irys) {
    try {
      // Mock Irys instance for testing
      irys = {
        address: "0x742d35Cc6634C0532925a3b8D4C9db96590c6C87", // Mock address
        upload: async (data, options) => {
          console.log("Mock Irys upload:", data, options);
          return { id: "mock-tx-" + Date.now() };
        }
      };
      console.log("Connected to Mock Irys network");
    } catch (error) {
      console.error("Failed to connect to Mock Irys:", error);
      throw error;
    }
  }
  return irys;
}

export async function uploadScore(scoreData) {
  try {
    const irysInstance = await getIrys();
    
    // Mock upload to Irys
    const response = await irysInstance.upload(JSON.stringify(scoreData), {
      tags: [
        { name: "App", value: "IrysReflex" },
        { name: "Tool", value: "ReactionTime" },
        { name: "Content-Type", value: "application/json" },
        { name: "Player", value: scoreData.player },
        { name: "Username", value: scoreData.username }
      ]
    });

    console.log("Score uploaded to Mock Irys:", response.id);
    return response.id;
  } catch (error) {
    console.error("Error uploading score to Mock Irys:", error);
    throw error;
  }
}

export async function getWalletAddress() {
  try {
    const irysInstance = await getIrys();
    return irysInstance.address;
  } catch (error) {
    console.error("Error getting wallet address:", error);
    throw error;
  }
}

export function getIrysExplorerUrl(txId) {
  const gateway = process.env.REACT_APP_GATEWAY_URL || "https://gateway.irys.xyz";
  return `${gateway}/${txId}`;
}