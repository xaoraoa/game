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

export async function checkWalletConnection() {
  if (!window.ethereum) {
    return { connected: false, error: "MetaMask not installed" };
  }
  
  try {
    const accounts = await window.ethereum.request({ method: 'eth_accounts' });
    if (accounts.length > 0) {
      return { connected: true, address: accounts[0] };
    }
    return { connected: false, error: "No accounts connected" };
  } catch (error) {
    return { connected: false, error: error.message };
  }
}

export async function connectWallet() {
  if (!window.ethereum) {
    throw new Error("MetaMask not installed. Please install MetaMask to connect your wallet.");
  }
  
  try {
    const accounts = await window.ethereum.request({ method: 'eth_requestAccounts' });
    if (accounts.length === 0) {
      throw new Error("No accounts found. Please check your MetaMask.");
    }
    
    const provider = new ethers.BrowserProvider(window.ethereum);
    const signer = await provider.getSigner();
    const address = await signer.getAddress();
    
    return {
      connected: true,
      address: address,
      signer: signer
    };
  } catch (error) {
    if (error.code === 4001) {
      throw new Error("User rejected the connection request");
    }
    throw new Error(`Failed to connect wallet: ${error.message}`);
  }
}

export async function getMetaMaskWallet() {
  const connection = await connectWallet();
  return {
    address: connection.address,
    signMessage: async (message) => {
      return await connection.signer.signMessage(message);
    }
  };
}

export async function checkIrysBalance() {
  try {
    const backendUrl = process.env.REACT_APP_BACKEND_URL;
    const response = await fetch(`${backendUrl}/api/irys/balance`);
    const data = await response.json();
    
    if (response.ok) {
      return {
        success: true,
        balance: data.balance,
        address: data.address,
        network: data.network
      };
    } else {
      return {
        success: false,
        error: data.detail || "Failed to check balance"
      };
    }
  } catch (error) {
    return {
      success: false,
      error: `Network error: ${error.message}`
    };
  }
}

export async function fundIrysAccount(amount = 10000) {
  try {
    const backendUrl = process.env.REACT_APP_BACKEND_URL;
    const response = await fetch(`${backendUrl}/api/irys/fund`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ amount })
    });
    
    const data = await response.json();
    
    if (response.ok) {
      return {
        success: true,
        transaction: data.transaction,
        amount: data.amount,
        message: data.message
      };
    } else {
      return {
        success: false,
        error: data.detail || "Funding failed",
        needsFaucet: response.status === 402
      };
    }
  } catch (error) {
    return {
      success: false,
      error: `Network error: ${error.message}`
    };
  }
}

export async function getNetworkInfo() {
  try {
    const backendUrl = process.env.REACT_APP_BACKEND_URL;
    const response = await fetch(`${backendUrl}/api/irys/network-info`);
    const data = await response.json();
    
    if (response.ok) {
      return {
        success: true,
        network: data.network,
        config: data.config,
        account: data.account,
        clientStatus: data.client_status
      };
    } else {
      return {
        success: false,
        error: "Failed to get network info"
      };
    }
  } catch (error) {
    return {
      success: false,
      error: `Network error: ${error.message}`
    };
  }
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
    
    if (response.ok && result.success) {
      console.log("Score uploaded to Irys:", result.tx_id);
      return result.tx_id;
    } else {
      // Handle specific error cases
      if (response.status === 402) {
        throw new Error("Insufficient balance. Please fund your account with IRYS tokens at https://irys.xyz/faucet");
      }
      throw new Error(result.detail || result.error || "Upload failed");
    }
  } catch (error) {
    console.error("Error uploading score to Irys:", error);
    throw error;
  }
}

export async function getWalletAddress() {
  try {
    // First try to get connected wallet
    const walletCheck = await checkWalletConnection();
    if (walletCheck.connected) {
      return walletCheck.address;
    }
    
    // If no wallet connected, try to connect
    if (window.ethereum) {
      const connection = await connectWallet();
      return connection.address;
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