import React, { useState, useEffect } from 'react';
import { getMetaMaskWallet, getNetworkInfo } from '../lib/irys';

const WalletConnection = ({ onWalletConnected, onWalletDisconnected }) => {
  const [walletAddress, setWalletAddress] = useState(null);
  const [isConnecting, setIsConnecting] = useState(false);
  const [networkInfo, setNetworkInfo] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Load network info
    getNetworkInfo().then(setNetworkInfo);
    
    // Check if wallet is already connected
    checkExistingConnection();
  }, []);

  const checkExistingConnection = async () => {
    try {
      if (window.ethereum) {
        const accounts = await window.ethereum.request({ method: 'eth_accounts' });
        if (accounts.length > 0) {
          const wallet = await getMetaMaskWallet();
          setWalletAddress(wallet.address);
          onWalletConnected(wallet);
        }
      }
    } catch (error) {
      console.error('Error checking existing wallet connection:', error);
    }
  };

  const connectWallet = async () => {
    setIsConnecting(true);
    setError(null);
    
    try {
      if (!window.ethereum) {
        throw new Error('MetaMask not installed. Please install MetaMask to continue.');
      }

      const wallet = await getMetaMaskWallet();
      setWalletAddress(wallet.address);
      onWalletConnected(wallet);
      
      // Listen for account changes
      window.ethereum.on('accountsChanged', handleAccountsChanged);
      window.ethereum.on('chainChanged', handleChainChanged);
      
    } catch (error) {
      setError(error.message);
      console.error('Wallet connection failed:', error);
    } finally {
      setIsConnecting(false);
    }
  };

  const disconnectWallet = () => {
    setWalletAddress(null);
    onWalletDisconnected();
    
    // Remove event listeners
    if (window.ethereum) {
      window.ethereum.removeListener('accountsChanged', handleAccountsChanged);
      window.ethereum.removeListener('chainChanged', handleChainChanged);
    }
  };

  const handleAccountsChanged = (accounts) => {
    if (accounts.length === 0) {
      disconnectWallet();
    } else {
      // Account changed, reconnect
      connectWallet();
    }
  };

  const handleChainChanged = (chainId) => {
    // Chain changed, might need to reconnect
    console.log('Chain changed:', chainId);
  };

  const truncateAddress = (address) => {
    if (!address) return '';
    return `${address.slice(0, 6)}...${address.slice(-4)}`;
  };

  return (
    <div className="wallet-connection">
      {!walletAddress ? (
        <div className="connect-wallet-section">
          <button
            onClick={connectWallet}
            disabled={isConnecting}
            className="connect-wallet-btn"
          >
            {isConnecting ? (
              <>
                <div className="spinner"></div>
                Connecting...
              </>
            ) : (
              <>
                <span className="wallet-icon">🦊</span>
                Connect MetaMask
              </>
            )}
          </button>
          
          {error && (
            <div className="error-message">
              <span className="error-icon">⚠️</span>
              {error}
            </div>
          )}
          
          <div className="network-info">
            <p>Network: {networkInfo?.name || 'Loading...'}</p>
            <p>Chain: {networkInfo?.chainId || 'Unknown'}</p>
          </div>
        </div>
      ) : (
        <div className="wallet-connected">
          <div className="wallet-info">
            <div className="wallet-address">
              <span className="address-label">Connected:</span>
              <span className="address-value">{truncateAddress(walletAddress)}</span>
            </div>
            <button
              onClick={disconnectWallet}
              className="disconnect-btn"
              title="Disconnect wallet"
            >
              ×
            </button>
          </div>
          
          <div className="wallet-status">
            <span className="status-dot connected"></span>
            <span className="status-text">Ready to play</span>
          </div>
        </div>
      )}
    </div>
  );
};

export default WalletConnection;