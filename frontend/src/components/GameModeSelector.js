import React from 'react';

const GameModeSelector = ({ gameModes, selectedGameMode, onSelectMode }) => {
  return (
    <div className="game-mode-section">
      <h3 className="game-mode-title">Select Game Mode</h3>
      <div className="game-mode-grid">
        {gameModes.map((mode) => (
          <div
            key={mode.id}
            className={`game-mode-card ${selectedGameMode === mode.id ? 'selected' : ''}`}
            onClick={() => onSelectMode(mode.id)}
          >
            <div className="game-mode-icon">{mode.icon}</div>
            <div className="game-mode-name">{mode.name}</div>
            <div className="game-mode-description">{mode.description}</div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default GameModeSelector;