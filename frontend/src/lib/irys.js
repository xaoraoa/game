// Backend-only Irys integration to avoid webpack issues
import { ethers } from "ethers";

// Network configurations
const NETWORKS = {
  testnet: {
    name: "Irys Testnet",
    url: "https://node2.irys.xyz",
    token: "ethereum",
    rpcUrl: "https://rpc.sepolia.org",
    chainId: 11155111,
    gateway: "https://gateway.irys.xyz"
  },
  mainnet: {
    name: "Irys Mainnet", 
    url: "https://node1.irys.xyz",
    token: "ethereum",
    rpcUrl: "https://eth.llamarpc.com",
    chainId: 1,
    gateway: "https://gateway.irys.xyz"
  }
};

export async function getMetaMaskWallet() {
  if (!window.ethereum) {
    throw new Error("MetaMask not installed");
  }
  
  await window.ethereum.request({ method: 'eth_requestAccounts' });
  const provider = new ethers.BrowserProvider(window.ethereum);
  const signer = await provider.getSigner();
  
  return {
    address: await signer.getAddress(),
    signMessage: async (message) => {
      return await signer.signMessage(message);
    }
  };
}

export async function uploadScore(scoreData, useUserWallet = false) {
  try {
    const backendUrl = process.env.REACT_APP_BACKEND_URL;
    
    // Always use backend for Irys operations to avoid webpack issues
    const response = await fetch(`${backendUrl}/api/irys/upload`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        data: JSON.stringify(scoreData),
        tags: [
          { name: "App", value: "IrysReflex" },
          { name: "Tool", value: "ReactionTime" },
          { name: "Content-Type", value: "application/json" },
          { name: "Player", value: scoreData.player },
          { name: "Username", value: scoreData.username },
          { name: "GameMode", value: scoreData.game_mode || "classic" },
          { name: "Timestamp", value: scoreData.timestamp }
        ],
        player_address: scoreData.player
      })
    });
    
    const result = await response.json();
    
    if (result.success) {
      console.log("Score uploaded to Irys:", result.tx_id);
      return result.tx_id;
    } else {
      throw new Error(result.error || "Upload failed");
    }
  } catch (error) {
    console.error("Error uploading score to Irys:", error);
    throw error;
  }
}

export async function getWalletAddress() {
  try {
    if (window.ethereum) {
      const wallet = await getMetaMaskWallet();
      return wallet.address;
    } else {
      // Fallback to backend wallet
      const backendUrl = process.env.REACT_APP_BACKEND_URL;
      const response = await fetch(`${backendUrl}/api/irys/public-key`);
      const { publicKey } = await response.json();
      return publicKey;
    }
  } catch (error) {
    console.error("Error getting wallet address:", error);
    throw error;
  }
}

export function getIrysExplorerUrl(txId) {
  const network = process.env.REACT_APP_IRYS_NETWORK || 'testnet';
  const config = NETWORKS[network];
  return `${config.gateway}/${txId}`;
}

export async function getNetworkInfo() {
  const network = process.env.REACT_APP_IRYS_NETWORK || 'testnet';
  return NETWORKS[network];
}