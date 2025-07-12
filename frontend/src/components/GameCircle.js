import React from 'react';

const GameCircle = ({ 
  gameState, 
  selectedGameMode, 
  sequenceCount, 
  totalSequenceTargets, 
  enduranceTimeLeft, 
  enduranceScore, 
  penalty,
  getDisplayTime,
  getGameModeDisplayName,
  onCircleClick 
}) => {
  return (
    <div className="game-container">
      <div 
        className={`game-circle ${gameState === 'flashed' ? 'flashed' : ''} ${gameState === 'ready' ? 'ready' : ''} ${selectedGameMode === 'precision' ? 'precision' : ''}`}
        onClick={onCircleClick}
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
  );
};

export default GameCircle;