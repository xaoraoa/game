import React, { useState, useEffect, useRef } from 'react';
import toast, { Toaster } from 'react-hot-toast';
import { uploadScore, getWalletAddress, getIrysExplorerUrl } from './lib/irys';
import './App.css';

interface LeaderboardEntry {
  id: string;
  player: string;
  username: string;
  time: number;
  penalty: boolean;
  timestamp: string;
  tx_id?: string;
  verified: boolean;
}

const App: React.FC = () => {
  const [gameState, setGameState] = useState<'waiting' | 'ready' | 'flashed' | 'finished'>('waiting');
  const [reactionTime, setReactionTime] = useState<number | null>(null);
  const [penalty, setPenalty] = useState<boolean>(false);
  const [username, setUsername] = useState<string>('');
  const [walletAddress, setWalletAddress] = useState<string>('');
  const [leaderboard, setLeaderboard] = useState<LeaderboardEntry[]>([]);
  const [uploading, setUploading] = useState<boolean>(false);
  const [lastTxId, setLastTxId] = useState<string>('');
  const [gameStarted, setGameStarted] = useState<boolean>(false);
  
  const gameRef = useRef<HTMLDivElement>(null);
  const startTimeRef = useRef<number | null>(null);
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);

  // Initialize Web Audio API
  useEffect(() => {
    audioContextRef.current = new (window.AudioContext || (window as any).webkitAudioContext)();
  }, []);

  // Initialize wallet address on component mount
  useEffect(() => {
    const initializeWallet = async () => {
      try {
        const address = await getWalletAddress();
        setWalletAddress(address);
        toast.success('Wallet connected successfully!');
      } catch (error) {
        console.error('Failed to get wallet address:', error);
        toast.error('Failed to connect to wallet. Please check your configuration.');
      }
    };

    initializeWallet();
    fetchLeaderboard();
  }, []);

  const playPingSound = () => {
    if (!audioContextRef.current) return;
    
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

  const startGame = () => {
    if (!username.trim()) {
      toast.error('Please enter a username before starting the game!');
      return;
    }

    setGameState('ready');
    setPenalty(false);
    setReactionTime(null);
    setGameStarted(true);
    
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
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    } else if (gameState === 'flashed') {
      // Calculate reaction time
      const endTime = Date.now();
      const reaction = endTime - (startTimeRef.current || 0);
      setReactionTime(reaction);
      setGameState('finished');
    }
  };

  const uploadToIrys = async () => {
    if (!username.trim()) {
      toast.error('Please enter a username');
      return;
    }

    if (!walletAddress) {
      toast.error('Wallet not connected');
      return;
    }

    if (reactionTime === null) {
      toast.error('No reaction time recorded');
      return;
    }

    setUploading(true);
    
    try {
      const scoreData = {
        player: walletAddress,
        username: username.trim(),
        time: reactionTime,
        penalty: penalty,
        timestamp: Date.now()
      };

      // Upload to Irys
      const txId = await uploadScore(scoreData);
      setLastTxId(txId);

      // Submit to backend
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/scores`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          player: walletAddress,
          username: username.trim(),
          time: reactionTime,
          penalty: penalty,
          timestamp: new Date().toISOString(),
          tx_id: txId
        }),
      });

      if (response.ok) {
        const result = await response.json();
        toast.success(`✅ Score saved to Irys! ${result.verified ? 'Verified' : 'Pending verification'}`);
        fetchLeaderboard();
      } else {
        throw new Error('Failed to save score to backend');
      }
    } catch (error) {
      console.error("Error uploading to Irys:", error);
      toast.error("Failed to upload score: " + (error as Error).message);
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

  const getDisplayTime = () => {
    if (penalty) return `${reactionTime}ms (+ 500ms penalty)`;
    return `${reactionTime}ms`;
  };

  const resetGame = () => {
    setGameState('waiting');
    setGameStarted(false);
    setPenalty(false);
    setReactionTime(null);
    setLastTxId('');
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }
  };

  return (
    <div className="app">
      <Toaster 
        position="top-center"
        toastOptions={{
          duration: 4000,
          style: {
            background: 'rgba(255, 255, 255, 0.1)',
            color: '#F8F8FF',
            border: '1px solid rgba(0, 255, 209, 0.3)',
            backdropFilter: 'blur(10px)',
          },
        }}
      />
      
      <div className="container">
        <header className="header">
          <h1 className="title">
            <span className="irys-gradient">Irys</span> Reflex
          </h1>
          <p className="subtitle">Test Your Reaction Time on the Blockchain</p>
        </header>

        <div className="wallet-section">
          <div className="wallet-info">
            <p><strong>Wallet:</strong> {walletAddress ? `${walletAddress.slice(0, 6)}...${walletAddress.slice(-4)}` : 'Not connected'}</p>
          </div>
          
          <div className="username-section">
            <input
              type="text"
              placeholder="Enter your username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="username-input"
              maxLength={20}
            />
          </div>
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
                <button onClick={resetGame} className="reset-btn">
                  Reset
                </button>
                {walletAddress && (
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
                    <div className="player-info">
                      <div className="username">{entry.username}</div>
                      <div className="address">
                        {entry.player.slice(0, 6)}...{entry.player.slice(-4)}
                      </div>
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
              href={getIrysExplorerUrl(lastTxId)}
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