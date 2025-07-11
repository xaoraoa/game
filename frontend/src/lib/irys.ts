import { Irys } from "@irys/sdk";

let irys: Irys | null = null;

export interface ScoreData {
  player: string;
  username: string;
  time: number;
  penalty: boolean;
  timestamp: number;
}

export async function getIrys(): Promise<Irys> {
  if (!irys) {
    try {
      // Get environment variables
      const network = process.env.VITE_IRYS_RPC_URL || "https://devnet.irys.xyz";
      const gateway = process.env.VITE_GATEWAY_URL || "https://gateway.irys.xyz";
      const privateKey = process.env.VITE_PRIVATE_KEY;

      if (!privateKey) {
        throw new Error("VITE_PRIVATE_KEY environment variable is required");
      }

      // Connect to Irys
      irys = new Irys({
        network,
        token: "ethereum",
        key: privateKey,
        config: {
          providerUrl: "https://rpc.sepolia.org"
        }
      });

      console.log("Connected to Irys network:", network);
    } catch (error) {
      console.error("Failed to connect to Irys:", error);
      throw error;
    }
  }
  return irys;
}

export async function uploadScore(scoreData: ScoreData): Promise<string> {
  try {
    const irysInstance = await getIrys();
    
    // Upload JSON data to Irys
    const response = await irysInstance.upload(JSON.stringify(scoreData), {
      tags: [
        { name: "App", value: "IrysReflex" },
        { name: "Tool", value: "ReactionTime" },
        { name: "Content-Type", value: "application/json" },
        { name: "Player", value: scoreData.player },
        { name: "Username", value: scoreData.username }
      ]
    });

    console.log("Score uploaded to Irys:", response.id);
    return response.id;
  } catch (error) {
    console.error("Error uploading score to Irys:", error);
    throw error;
  }
}

export async function getWalletAddress(): Promise<string> {
  try {
    const irysInstance = await getIrys();
    return irysInstance.address;
  } catch (error) {
    console.error("Error getting wallet address:", error);
    throw error;
  }
}

export function getIrysExplorerUrl(txId: string): string {
  const gateway = process.env.VITE_GATEWAY_URL || "https://gateway.irys.xyz";
  return `${gateway}/${txId}`;
}