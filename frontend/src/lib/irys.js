// Real Irys SDK implementation
import { Irys } from "@irys/sdk";
import { ethers } from "ethers";

let irys = null;

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

export async function getIrys(userWallet = null) {
  if (!irys) {
    try {
      const network = process.env.REACT_APP_IRYS_NETWORK || 'testnet';
      const config = NETWORKS[network];
      
      let wallet;
      
      if (userWallet) {
        // Use user's MetaMask wallet
        wallet = userWallet;
      } else {
        // Use app's backend wallet for server-side operations
        const backendUrl = process.env.REACT_APP_BACKEND_URL;
        
        // Get server's public key
        const response = await fetch(`${backendUrl}/api/irys/public-key`);
        const { publicKey } = await response.json();
        
        // Create a wallet interface that uses backend signing
        wallet = {
          address: publicKey,
          signMessage: async (message) => {
            const signResponse = await fetch(`${backendUrl}/api/irys/sign`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ message })
            });
            const { signature } = await signResponse.json();
            return signature;
          }
        };
      }
      
      // Initialize Irys
      irys = new Irys({
        url: config.url,
        token: config.token,
        wallet,
        config: {
          providerUrl: config.rpcUrl
        }
      });
      
      console.log(`Connected to ${config.name} network`);
      console.log(`Account: ${wallet.address}`);
      
    } catch (error) {
      console.error("Failed to connect to Irys:", error);
      throw error;
    }
  }
  return irys;
}

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
    let wallet = null;
    
    if (useUserWallet) {
      wallet = await getMetaMaskWallet();
    }
    
    const irysInstance = await getIrys(wallet);
    
    // Upload to Irys
    const response = await irysInstance.upload(JSON.stringify(scoreData), {
      tags: [
        { name: "App", value: "IrysReflex" },
        { name: "Tool", value: "ReactionTime" },
        { name: "Content-Type", value: "application/json" },
        { name: "Player", value: scoreData.player },
        { name: "Username", value: scoreData.username },
        { name: "GameMode", value: scoreData.game_mode || "classic" },
        { name: "Timestamp", value: scoreData.timestamp }
      ]
    });

    console.log("Score uploaded to Irys:", response.id);
    return response.id;
  } catch (error) {
    console.error("Error uploading score to Irys:", error);
    
    // Fallback to backend upload if Irys fails
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL;
      const backendResponse = await fetch(`${backendUrl}/api/irys/upload`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          data: JSON.stringify(scoreData),
          tags: [
            { name: "App", value: "IrysReflex" },
            { name: "Tool", value: "ReactionTime" },
            { name: "Content-Type", value: "application/json" },
            { name: "Player", value: scoreData.player },
            { name: "Username", value: scoreData.username }
          ],
          player_address: scoreData.player
        })
      });
      
      const result = await backendResponse.json();
      console.log("Score uploaded via backend:", result.tx_id);
      return result.tx_id;
    } catch (backendError) {
      console.error("Backend upload also failed:", backendError);
      throw error;
    }
  }
}

export async function getWalletAddress() {
  try {
    if (window.ethereum) {
      const wallet = await getMetaMaskWallet();
      return wallet.address;
    } else {
      // Fallback to backend wallet
      const irysInstance = await getIrys();
      return irysInstance.address;
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