import React, { useState, useEffect, useRef } from 'react';
import toast, { Toaster } from 'react-hot-toast';
import { 
  uploadScore, 
  getWalletAddress, 
  getIrysExplorerUrl, 
  checkWalletConnection, 
  connectWallet,
  checkIrysBalance,
  fundIrysAccount,
  getNetworkInfo
} from './lib/irys';
import { initKeepAlive } from './utils/keepAlive';
import TwitterShare from './components/TwitterShare';
import './App.css';

const App = () => {
  const [gameState, setGameState] = useState('waiting');
  const [reactionTime, setReactionTime] = useState(null);
  const [penalty, setPenalty] = useState(false);
  const [username, setUsername] = useState('');
  const [walletAddress, setWalletAddress] = useState('');
  const [walletConnected, setWalletConnected] = useState(false);
  const [walletConnecting, setWalletConnecting] = useState(false);
  const [irysBalance, setIrysBalance] = useState(null);
  const [networkInfo, setNetworkInfo] = useState(null);
  const [leaderboard, setLeaderboard] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [lastTxId, setLastTxId] = useState('');
  const [gameStarted, setGameStarted] = useState(false);
  const [selectedGameMode, setSelectedGameMode] = useState('classic');
  const [gameModes, setGameModes] = useState([]);
  
  // New state for different game modes
  const [sequenceCount, setSequenceCount] = useState(0);
  const [sequenceTimes, setSequenceTimes] = useState([]);
  const [totalSequenceTargets, setTotalSequenceTargets] = useState(3);
  const [enduranceScore, setEnduranceScore] = useState(0);
  const [enduranceTimeLeft, setEnduranceTimeLeft] = useState(60);
  const [enduranceTimer, setEnduranceTimer] = useState(null);
  const [precisionMissed, setPrecisionMissed] = useState(0);
  const [precisionHits, setPrecisionHits] = useState(0);
  
  const gameRef = useRef(null);
  const startTimeRef = useRef(null);
  const timeoutRef = useRef(null);
  const audioContextRef = useRef(null);

  // Initialize Web Audio API and keep-alive service
  useEffect(() => {
    audioContextRef.current = new (window.AudioContext || window.webkitAudioContext)();
    
    // Initialize keep-alive service to prevent Render dyno sleep
    const cleanupKeepAlive = initKeepAlive();
    
    // Cleanup function
    return () => {
      if (cleanupKeepAlive) {
        cleanupKeepAlive();
      }
    };
  }, []);

  // Initialize components on mount
  useEffect(() => {
    checkInitialWalletConnection();
    fetchGameModes();
    fetchLeaderboard();
    fetchNetworkInfo();
  }, []);

  const checkInitialWalletConnection = async () => {
    try {
      const walletCheck = await checkWalletConnection();
      if (walletCheck.connected) {
        setWalletAddress(walletCheck.address);
        setWalletConnected(true);
        await checkBalance();
        toast.success('Wallet connected!');
      }
    } catch (error) {
      console.error('Initial wallet check failed:', error);
    }
  };

  const handleWalletConnect = async () => {
    if (walletConnecting) return;
    
    setWalletConnecting(true);
    try {
      const connection = await connectWallet();
      setWalletAddress(connection.address);
      setWalletConnected(true);
      await checkBalance();
      toast.success('Wallet connected successfully!');
    } catch (error) {
      console.error('Wallet connection failed:', error);
      toast.error(error.message || 'Failed to connect wallet');
    } finally {
      setWalletConnecting(false);
    }
  };

  const checkBalance = async () => {
    try {
      const balanceResult = await checkIrysBalance();
      if (balanceResult.success) {
        setIrysBalance(balanceResult.balance);
      } else {
        console.error('Balance check failed:', balanceResult.error);
      }
    } catch (error) {
      console.error('Balance check error:', error);
    }
  };

  const handleFundAccount = async () => {
    try {
      toast.loading('Funding account...', { id: 'funding' });
      const fundResult = await fundIrysAccount(10000);
      
      if (fundResult.success) {
        toast.success(fundResult.message, { id: 'funding' });
        await checkBalance(); // Refresh balance
      } else {
        if (fundResult.needsFaucet) {
          toast.error('Please get testnet tokens from the faucet first', { id: 'funding' });
          // Open faucet in new tab
          if (networkInfo?.config?.faucet_url) {
            window.open(networkInfo.config.faucet_url, '_blank');
          }
        } else {
          toast.error(fundResult.error, { id: 'funding' });
        }
      }
    } catch (error) {
      toast.error('Funding failed: ' + error.message, { id: 'funding' });
    }
  };

  const fetchNetworkInfo = async () => {
    try {
      const netInfo = await getNetworkInfo();
      if (netInfo.success) {
        setNetworkInfo(netInfo);
      }
    } catch (error) {
      console.error('Failed to fetch network info:', error);
    }
  };

  const fetchGameModes = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/game-modes`);
      if (response.ok) {
        const data = await response.json();
        setGameModes(data.modes);
      }
    } catch (error) {
      console.error('Error fetching game modes:', error);
    }
  };

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

    // Reset all game state
    setGameState('ready');
    setPenalty(false);
    setReactionTime(null);
    setGameStarted(true);
    
    // Reset mode-specific state
    setSequenceCount(0);
    setSequenceTimes([]);
    setEnduranceScore(0);
    setEnduranceTimeLeft(60);
    setPrecisionMissed(0);
    setPrecisionHits(0);
    
    // Start game based on selected mode
    switch (selectedGameMode) {
      case 'classic':
        startClassicGame();
        break;
      case 'sequence':
        startSequenceGame();
        break;
      case 'endurance':
        startEnduranceGame();
        break;
      case 'precision':
        startPrecisionGame();
        break;
      default:
        startClassicGame();
    }
  };

  const startClassicGame = () => {
    // Random delay between 1-5 seconds
    const delay = Math.random() * 4000 + 1000;
    
    timeoutRef.current = setTimeout(() => {
      setGameState('flashed');
      startTimeRef.current = Date.now();
      playPingSound();
    }, delay);
  };

  const startSequenceGame = () => {
    setSequenceCount(0);
    setSequenceTimes([]);
    // Start first target
    const delay = Math.random() * 2000 + 1000;
    
    timeoutRef.current = setTimeout(() => {
      setGameState('flashed');
      startTimeRef.current = Date.now();
      playPingSound();
    }, delay);
  };

  const startEnduranceGame = () => {
    setEnduranceScore(0);
    setEnduranceTimeLeft(60);
    
    // Start countdown timer
    const timer = setInterval(() => {
      setEnduranceTimeLeft(prev => {
        if (prev <= 1) {
          clearInterval(timer);
          setGameState('finished');
          setReactionTime(enduranceScore); // Use score as "time" for display
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
    
    setEnduranceTimer(timer);
    
    // Start first target
    const delay = Math.random() * 2000 + 500;
    timeoutRef.current = setTimeout(() => {
      setGameState('flashed');
      startTimeRef.current = Date.now();
      playPingSound();
    }, delay);
  };

  const startPrecisionGame = () => {
    setPrecisionMissed(0);
    setPrecisionHits(0);
    
    // Start with slightly longer delay for precision mode
    const delay = Math.random() * 3000 + 1500;
    
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
      if (enduranceTimer) {
        clearInterval(enduranceTimer);
      }
    } else if (gameState === 'flashed') {
      // Calculate reaction time
      const endTime = Date.now();
      const reaction = endTime - (startTimeRef.current || 0);
      
      handleGameModeClick(reaction);
    }
  };

  const handleGameModeClick = (reaction) => {
    switch (selectedGameMode) {
      case 'classic':
        handleClassicClick(reaction);
        break;
      case 'sequence':
        handleSequenceClick(reaction);
        break;
      case 'endurance':
        handleEnduranceClick(reaction);
        break;
      case 'precision':
        handlePrecisionClick(reaction);
        break;
      default:
        handleClassicClick(reaction);
    }
  };

  const handleClassicClick = (reaction) => {
    setReactionTime(reaction);
    setGameState('finished');
  };

  const handleSequenceClick = (reaction) => {
    const newSequenceTimes = [...sequenceTimes, reaction];
    setSequenceTimes(newSequenceTimes);
    
    if (newSequenceTimes.length >= totalSequenceTargets) {
      // Sequence complete
      const averageTime = Math.round(newSequenceTimes.reduce((a, b) => a + b, 0) / newSequenceTimes.length);
      setReactionTime(averageTime);
      setGameState('finished');
    } else {
      // Next target in sequence
      setSequenceCount(newSequenceTimes.length);
      setGameState('ready');
      
      // Short delay before next target
      const delay = Math.random() * 1500 + 500;
      timeoutRef.current = setTimeout(() => {
        setGameState('flashed');
        startTimeRef.current = Date.now();
        playPingSound();
      }, delay);
    }
  };

  const handleEnduranceClick = (reaction) => {
    setEnduranceScore(prev => prev + 1);
    setGameState('ready');
    
    // Quick next target
    const delay = Math.random() * 1500 + 300;
    timeoutRef.current = setTimeout(() => {
      if (enduranceTimeLeft > 0) {
        setGameState('flashed');
        startTimeRef.current = Date.now();
        playPingSound();
      }
    }, delay);
  };

  const handlePrecisionClick = (reaction) => {
    setPrecisionHits(prev => prev + 1);
    setReactionTime(reaction);
    setGameState('finished');
  };

  const handleCircleMiss = () => {
    if (selectedGameMode === 'precision') {
      setPrecisionMissed(prev => prev + 1);
      toast.error('Missed! Try to be more precise.');
    }
  };

  const uploadToIrys = async () => {
    if (!username.trim()) {
      toast.error('Please enter a username');
      return;
    }

    if (!walletConnected || !walletAddress) {
      toast.error('Please connect your wallet first');
      return;
    }

    if (reactionTime === null && selectedGameMode !== 'endurance') {
      toast.error('No reaction time recorded');
      return;
    }

    // Check balance before uploading - skip for testnet/devnet (free uploads)
    const isTestNetwork = networkInfo?.network === 'testnet' || networkInfo?.network === 'devnet';
    if (!isTestNetwork && irysBalance !== null && irysBalance < 1000) {
      toast.error('Insufficient balance. Please fund your account with IRYS tokens.', {
        duration: 6000,
        action: {
          label: 'Fund Account',
          onClick: handleFundAccount
        }
      });
      return;
    }

    setUploading(true);
    
    try {
      const scoreData = {
        player: walletAddress,
        username: username.trim(),
        time: reactionTime,
        penalty: penalty,
        timestamp: Date.now(),
        game_mode: selectedGameMode
      };

      // Add mode-specific data
      if (selectedGameMode === 'sequence') {
        scoreData.sequence_times = sequenceTimes;
        scoreData.total_targets = totalSequenceTargets;
      } else if (selectedGameMode === 'endurance') {
        scoreData.hits_count = enduranceScore;
        scoreData.time = enduranceScore; // For endurance, "time" is actually hits
      } else if (selectedGameMode === 'precision') {
        scoreData.accuracy = precisionHits / (precisionHits + precisionMissed) * 100;
        scoreData.total_targets = precisionHits + precisionMissed;
      }

      // Upload to Irys
      toast.loading('Uploading to Irys blockchain...', { id: 'upload' });
      const txId = await uploadScore(scoreData);
      setLastTxId(txId);
      toast.success('✅ Uploaded to Irys!', { id: 'upload' });

      // Submit to backend
      toast.loading('Saving score...', { id: 'save' });
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
          tx_id: txId,
          game_mode: selectedGameMode,
          hits_count: selectedGameMode === 'endurance' ? enduranceScore : null,
          accuracy: selectedGameMode === 'precision' ? (precisionHits / (precisionHits + precisionMissed) * 100) : null,
          sequence_times: selectedGameMode === 'sequence' ? sequenceTimes : null,
          total_targets: selectedGameMode === 'sequence' ? totalSequenceTargets : (selectedGameMode === 'precision' ? precisionHits + precisionMissed : null)
        }),
      });

      if (response.ok) {
        const result = await response.json();
        toast.success(`🎉 Score saved! ${result.verified ? 'Verified on Irys' : 'Pending verification'}`, { id: 'save' });
        fetchLeaderboard();
        // Refresh balance after successful upload
        await checkBalance();
      } else {
        throw new Error('Failed to save score to backend');
      }
    } catch (error) {
      console.error("Error uploading to Irys:", error);
      
      // Handle specific error cases
      if (error.message.includes('insufficient balance') || error.message.includes('Insufficient balance')) {
        toast.error('💸 Insufficient IRYS balance! Please fund your account.', { 
          id: 'upload',
          duration: 6000,
          action: {
            label: 'Get Tokens',
            onClick: () => {
              if (networkInfo?.config?.faucet_url) {
                window.open(networkInfo.config.faucet_url, '_blank');
              }
            }
          }
        });
      } else if (error.message.includes('rejected')) {
        toast.error('Transaction was rejected by user', { id: 'upload' });
      } else {
        toast.error("❌ Failed to upload: " + error.message, { id: 'upload' });
      }
    } finally {
      setUploading(false);
    }
  };

  const fetchLeaderboard = async (gameMode = null) => {
    try {
      const mode = gameMode || selectedGameMode;
      const url = `${process.env.REACT_APP_BACKEND_URL}/api/leaderboard${mode ? `?game_mode=${mode}` : ''}`;
      const response = await fetch(url);
      if (response.ok) {
        const data = await response.json();
        setLeaderboard(data);
      }
    } catch (error) {
      console.error("Error fetching leaderboard:", error);
    }
  };

  const getDisplayTime = () => {
    if (selectedGameMode === 'endurance') {
      return `${enduranceScore} hits`;
    } else if (selectedGameMode === 'sequence') {
      return `${reactionTime}ms avg (${sequenceTimes.length}/${totalSequenceTargets})`;
    } else if (selectedGameMode === 'precision') {
      const accuracy = precisionHits / (precisionHits + precisionMissed) * 100;
      return `${reactionTime}ms (${accuracy.toFixed(1)}% accuracy)`;
    }
    
    if (penalty) return `${reactionTime}ms (+ 500ms penalty)`;
    return `${reactionTime}ms`;
  };

  const getGameModeDisplayName = (mode) => {
    const gameModeObj = gameModes.find(gm => gm.id === mode);
    return gameModeObj ? gameModeObj.name : mode;
  };

  const resetGame = () => {
    setGameState('waiting');
    setGameStarted(false);
    setPenalty(false);
    setReactionTime(null);
    setLastTxId('');
    
    // Reset mode-specific state
    setSequenceCount(0);
    setSequenceTimes([]);
    setEnduranceScore(0);
    setEnduranceTimeLeft(60);
    setPrecisionMissed(0);
    setPrecisionHits(0);
    
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }
    if (enduranceTimer) {
      clearInterval(enduranceTimer);
    }
  };

  // Update leaderboard when game mode changes
  useEffect(() => {
    if (selectedGameMode) {
      fetchLeaderboard(selectedGameMode);
    }
  }, [selectedGameMode]);

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
          {!walletConnected ? (
            <div className="wallet-connect">
              <div className="wallet-status">
                <h3>🔗 Connect Your Wallet</h3>
                <p>Connect MetaMask to save your scores permanently on Irys blockchain</p>
              </div>
              
              <button 
                onClick={handleWalletConnect}
                disabled={walletConnecting}
                className="connect-wallet-btn"
              >
                {walletConnecting ? '🔄 Connecting...' : '🦊 Connect MetaMask'}
              </button>
              
              {!window.ethereum && (
                <div className="metamask-warning">
                  <p>⚠️ MetaMask not detected. <a href="https://metamask.io" target="_blank" rel="noopener noreferrer">Install MetaMask</a></p>
                </div>
              )}
            </div>
          ) : (
            <div className="wallet-connected">
              <div className="wallet-info">
                <div className="wallet-address">
                  <strong>✅ Wallet Connected:</strong>
                  <span className="address">{walletAddress.slice(0, 6)}...{walletAddress.slice(-4)}</span>
                </div>
                
                <div className="irys-balance">
                  <strong>Irys Balance:</strong>
                  <span className="balance">
                    {irysBalance !== null ? `${irysBalance} wei` : 'Loading...'}
                  </span>
                  {irysBalance !== null && irysBalance < 1000 && (
                    <button 
                      onClick={handleFundAccount}
                      className="fund-btn"
                      title="Fund your account to save scores"
                    >
                      💰 Fund Account
                    </button>
                  )}
                </div>
                
                {networkInfo && (
                  <div className="network-info">
                    <strong>Network:</strong>
                    <span>{networkInfo.network} ({networkInfo.config?.name})</span>
                    {networkInfo.config?.faucet_url && (
                      <a 
                        href={networkInfo.config.faucet_url} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="faucet-link"
                      >
                        🚰 Get Testnet Tokens
                      </a>
                    )}
                  </div>
                )}
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
          )}
        </div>

        <div className="game-mode-section">
          <h3 className="game-mode-title">Select Game Mode</h3>
          <div className="game-mode-grid">
            {Array.isArray(gameModes) && gameModes.length
              ? gameModes.map((mode) => (
                <div
                  key={mode.id}
                  className={`game-mode-card ${selectedGameMode === mode.id ? 'selected' : ''}`}
                  onClick={() => setSelectedGameMode(mode.id)}
                >
                  <div className="game-mode-icon">{mode.icon}</div>
                  <div className="game-mode-name">{mode.name}</div>
                  <div className="game-mode-description">{mode.description}</div>
                </div>
              ))
              : <p>No game modes available</p>
            }
          </div>
        </div>

        <div className="game-section">
          <div className="game-container">
            <div 
              ref={gameRef}
              className={`game-circle ${gameState === 'flashed' ? 'flashed' : ''} ${gameState === 'ready' ? 'ready' : ''} ${selectedGameMode === 'precision' ? 'precision' : ''}`}
              onClick={handleCircleClick}
            >
              {gameState === 'waiting' && (
                <span>
                  Click to Start<br />
                  <small>{getGameModeDisplayName(selectedGameMode)} Mode</small>
                </span>
              )}
              {gameState === 'ready' && (
                <span>
                  {selectedGameMode === 'sequence' && `Target ${sequenceCount + 1}/${totalSequenceTargets}`}<br />
                  {selectedGameMode === 'endurance' && `${enduranceTimeLeft}s | ${enduranceScore} hits`}<br />
                  Wait for flash...
                </span>
              )}
              {gameState === 'flashed' && <span>CLICK NOW!</span>}
              {gameState === 'finished' && (
                <span>
                  {penalty ? 'Too Soon!' : (selectedGameMode === 'endurance' ? 'Time Up!' : 'Good!')}<br />
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
                {username && reactionTime && (
                  <TwitterShare
                    reactionTime={reactionTime}
                    gameMode={selectedGameMode}
                    username={username}
                    penalty={penalty}
                    enduranceScore={enduranceScore}
                    precisionAccuracy={precisionHits > 0 ? (precisionHits / (precisionHits + precisionMissed) * 100) : 0}
                    sequenceTimes={sequenceTimes}
                  />
                )}
                {/* Demo TwitterShare button for testing - always visible when game finished */}
                {gameState === 'finished' && reactionTime && (
                  <TwitterShare
                    reactionTime={reactionTime}
                    gameMode={selectedGameMode}
                    username={username || 'Anonymous'}
                    penalty={penalty}
                    enduranceScore={enduranceScore}
                    precisionAccuracy={precisionHits > 0 ? (precisionHits / (precisionHits + precisionMissed) * 100) : 0}
                    sequenceTimes={sequenceTimes}
                  />
                )}
              </div>
            )}
          </div>
        </div>

        <div className="leaderboard-section">
          <h2 className="leaderboard-title">🏆 Leaderboard - {getGameModeDisplayName(selectedGameMode)}</h2>
          <div className="leaderboard">
            {!Array.isArray(leaderboard) || leaderboard.length === 0 ? (
              <p className="no-scores">No scores yet for {getGameModeDisplayName(selectedGameMode)} mode. Be the first!</p>
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
                      {entry.game_mode === 'endurance' ? `${entry.time} hits` : 
                       entry.game_mode === 'precision' ? `${entry.time}ms (${entry.accuracy ? entry.accuracy.toFixed(1) : '0'}%)` :
                       `${entry.time}ms`}
                      {entry.penalty && ' (penalty)'}
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