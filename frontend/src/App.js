import React, { useState, useEffect, useRef } from 'react';
import './App.css';

const App = () => {
  const [gameState, setGameState] = useState('waiting'); // waiting, ready, flashed, finished
  const [reactionTime, setReactionTime] = useState(null);
  const [penalty, setPenalty] = useState(false);
  const [walletAddress, setWalletAddress] = useState('');
  const [isConnected, setIsConnected] = useState(false);
  const [leaderboard, setLeaderboard] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [lastTxId, setLastTxId] = useState('');
  
  const gameRef = useRef(null);
  const startTimeRef = useRef(null);
  const timeoutRef = useRef(null);
  const audioContextRef = useRef(null);

  // Initialize Web Audio API
  useEffect(() => {
    audioContextRef.current = new (window.AudioContext || window.webkitAudioContext)();
  }, []);

  const playPingSound = () => {
    const audioContext = audioContextRef.current;
    const oscillator = audioContext.createOscillator();
    const gainNode = audioContext.createGain();
    
    oscillator.connect(gainNode);
    gainNode.connect(audioContext.destination);
    
    oscillator.frequency.value = 800; // 800Hz tone
    oscillator.type = 'sine';
    
    gainNode.gain.setValueAtTime(0.1, audioContext.currentTime);
    gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.05);
    
    oscillator.start(audioContext.currentTime);
    oscillator.stop(audioContext.currentTime + 0.05);
  };

  const connectWallet = async () => {
    if (window.ethereum) {
      try {
        const accounts = await window.ethereum.request({ method: 'eth_requestAccounts' });
        setWalletAddress(accounts[0]);
        setIsConnected(true);
      } catch (error) {
        console.error("Error connecting wallet:", error);
        alert("Failed to connect wallet");
      }
    } else {
      alert('Please install MetaMask!');
    }
  };

  const startGame = () => {
    setGameState('ready');
    setPenalty(false);
    setReactionTime(null);
    
    // Random delay between 1-5 seconds
    const delay = Math.random() * 4000 + 1000;
    
    timeoutRef.current = setTimeout(() => {
      setGameState('flashed');
      startTimeRef.current = Date.now();
      playPingSound();
    }, delay);
  };

  const handleCircleClick = () => {
    if (gameState === 'ready') {
      // Too soon!
      setPenalty(true);
      setReactionTime(500); // 500ms penalty
      setGameState('finished');
      clearTimeout(timeoutRef.current);
    } else if (gameState === 'flashed') {
      // Calculate reaction time
      const endTime = Date.now();
      const reaction = endTime - startTimeRef.current;
      setReactionTime(reaction);
      setGameState('finished');
    }
  };

  const uploadToIrys = async () => {
    if (!isConnected) {
      alert('Please connect your wallet first');
      return;
    }

    setUploading(true);
    
    try {
      // Mock Irys upload for now - in a real implementation, you'd use the Irys SDK
      const scoreData = {
        player: walletAddress,
        time: reactionTime,
        penalty: penalty,
        timestamp: new Date().toISOString(),
        gameType: "IrysReflex"
      };

      // Simulate upload delay
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Mock transaction ID
      const mockTxId = 'mock_tx_' + Math.random().toString(36).substr(2, 9);
      setLastTxId(mockTxId);

      // Submit to backend
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/scores`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          player: walletAddress,
          time: reactionTime,
          penalty: penalty,
          timestamp: scoreData.timestamp,
          tx_id: mockTxId
        }),
      });

      if (response.ok) {
        const result = await response.json();
        alert(`✅ Score saved to Irys! ${result.verified ? 'Verified' : 'Pending verification'}`);
        fetchLeaderboard();
      } else {
        throw new Error('Failed to save score');
      }
    } catch (error) {
      console.error("Error uploading to Irys:", error);
      alert("Failed to upload score: " + error.message);
    } finally {
      setUploading(false);
    }
  };

  const fetchLeaderboard = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/leaderboard`);
      if (response.ok) {
        const data = await response.json();
        setLeaderboard(data);
      }
    } catch (error) {
      console.error("Error fetching leaderboard:", error);
    }
  };

  useEffect(() => {
    fetchLeaderboard();
  }, []);

  const getDisplayTime = () => {
    if (penalty) return `${reactionTime}ms (+ 500ms penalty)`;
    return `${reactionTime}ms`;
  };

  return (
    <div className="app">
      <div className="container">
        <header className="header">
          <h1 className="title">
            <span className="irys-gradient">Irys</span> Reflex
          </h1>
          <p className="subtitle">Test Your Reaction Time on the Blockchain</p>
        </header>

        <div className="wallet-section">
          {!isConnected ? (
            <button onClick={connectWallet} className="connect-btn">
              Connect Wallet
            </button>
          ) : (
            <div className="wallet-info">
              <p>Connected: {walletAddress.slice(0, 6)}...{walletAddress.slice(-4)}</p>
            </div>
          )}
        </div>

        <div className="game-section">
          <div className="game-container">
            <div 
              ref={gameRef}
              className={`game-circle ${gameState === 'flashed' ? 'flashed' : ''} ${gameState === 'ready' ? 'ready' : ''}`}
              onClick={handleCircleClick}
            >
              {gameState === 'waiting' && <span>Click to Start</span>}
              {gameState === 'ready' && <span>Wait for flash...</span>}
              {gameState === 'flashed' && <span>CLICK NOW!</span>}
              {gameState === 'finished' && (
                <span>
                  {penalty ? 'Too Soon!' : 'Good!'}<br />
                  {getDisplayTime()}
                </span>
              )}
            </div>
          </div>

          <div className="controls">
            {gameState === 'waiting' && (
              <button onClick={startGame} className="start-btn">
                Start Game
              </button>
            )}
            {gameState === 'finished' && (
              <div className="finished-controls">
                <button onClick={startGame} className="restart-btn">
                  Play Again
                </button>
                {isConnected && (
                  <button 
                    onClick={uploadToIrys} 
                    disabled={uploading}
                    className="save-btn"
                  >
                    {uploading ? 'Saving to Irys...' : 'Save to Irys'}
                  </button>
                )}
              </div>
            )}
          </div>
        </div>

        <div className="leaderboard-section">
          <h2 className="leaderboard-title">🏆 Leaderboard</h2>
          <div className="leaderboard">
            {leaderboard.length === 0 ? (
              <p className="no-scores">No scores yet. Be the first!</p>
            ) : (
              <div className="leaderboard-list">
                {leaderboard.map((entry, index) => (
                  <div key={entry.id} className="leaderboard-entry">
                    <div className="rank">#{index + 1}</div>
                    <div className="player">
                      {entry.player.slice(0, 6)}...{entry.player.slice(-4)}
                    </div>
                    <div className="time">
                      {entry.time}ms {entry.penalty && '(penalty)'}
                    </div>
                    <div className="verified">
                      {entry.verified ? '✅' : '⏳'}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {lastTxId && (
          <div className="tx-info">
            <p>Last transaction: {lastTxId}</p>
            <a 
              href={`https://devnet.irys.xyz/${lastTxId}`}
              target="_blank"
              rel="noopener noreferrer"
              className="tx-link"
            >
              View on Irys
            </a>
          </div>
        )}
      </div>
    </div>
  );
};

export default App;