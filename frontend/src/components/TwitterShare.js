import React, { useState } from 'react';
import html2canvas from 'html2canvas';
import toast from 'react-hot-toast';

const TwitterShare = ({ 
  reactionTime, 
  gameMode, 
  username, 
  penalty, 
  enduranceScore, 
  precisionAccuracy, 
  sequenceTimes 
}) => {
  const [isSharing, setIsSharing] = useState(false);

  const getShareText = () => {
    let text = `🎯 Just tested my reaction time on Irys Reflex!\n\n`;
    
    switch (gameMode) {
      case 'classic':
        text += `⚡ Classic Mode: ${reactionTime}ms${penalty ? ' (with penalty)' : ''}\n`;
        break;
      case 'sequence':
        const avgTime = sequenceTimes?.length ? 
          Math.round(sequenceTimes.reduce((a, b) => a + b, 0) / sequenceTimes.length) : reactionTime;
        text += `🔄 Sequence Mode: ${avgTime}ms average (${sequenceTimes?.length || 0} targets)\n`;
        break;
      case 'endurance':
        text += `⏱️ Endurance Mode: ${enduranceScore} hits in 60 seconds\n`;
        break;
      case 'precision':
        text += `🎪 Precision Mode: ${reactionTime}ms with ${precisionAccuracy?.toFixed(1) || 0}% accuracy\n`;
        break;
      default:
        text += `Reaction time: ${reactionTime}ms\n`;
    }
    
    text += `\nTest your reflexes on the blockchain! 🔗\n`;
    text += `#IrysReflex #ReactionTime #Blockchain #Gaming`;
    
    return text;
  };

  const captureAndShare = async () => {
    setIsSharing(true);
    try {
      // Find the game results area to capture
      const gameContainer = document.querySelector('.game-container');
      const gameCircle = document.querySelector('.game-circle');
      
      if (!gameContainer || !gameCircle) {
        throw new Error('Game elements not found');
      }

      // Create a custom capture area that includes results
      const captureElement = document.createElement('div');
      captureElement.style.cssText = `
        position: fixed;
        top: -10000px;
        left: -10000px;
        width: 600px;
        height: 400px;
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #3a007a 100%);
        padding: 40px;
        border-radius: 20px;
        color: white;
        font-family: 'Inter', sans-serif;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        z-index: 10000;
      `;

      captureElement.innerHTML = `
        <div style="text-align: center; margin-bottom: 30px;">
          <h1 style="background: linear-gradient(135deg, #00ffd1 0%, #7c3aed 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 32px; font-weight: bold; margin: 0 0 10px 0;">Irys Reflex</h1>
          <p style="color: #a0a0a0; margin: 0; font-size: 16px;">Reaction Time Test Results</p>
        </div>
        
        <div style="background: rgba(255, 255, 255, 0.1); backdrop-filter: blur(10px); border-radius: 15px; padding: 30px; margin: 20px 0; text-align: center; border: 1px solid rgba(255, 255, 255, 0.2);">
          <div style="font-size: 24px; font-weight: bold; margin-bottom: 10px;">👤 ${username}</div>
          <div style="font-size: 18px; color: #00ffd1; margin-bottom: 15px;">
            ${gameMode === 'classic' ? '🎯 Classic Mode' : 
              gameMode === 'sequence' ? '🔄 Sequence Mode' : 
              gameMode === 'endurance' ? '⏱️ Endurance Mode' : 
              '🎪 Precision Mode'}
          </div>
          <div style="font-size: 36px; font-weight: bold; color: #00ffd1; margin-bottom: 10px;">
            ${gameMode === 'endurance' ? `${enduranceScore} hits` : `${reactionTime}ms`}
          </div>
          ${penalty ? '<div style="color: #ff6b6b; font-size: 16px;">⚠️ Penalty Applied</div>' : ''}
          ${gameMode === 'precision' && precisionAccuracy ? 
            `<div style="color: #ffd700; font-size: 18px;">${precisionAccuracy.toFixed(1)}% Accuracy</div>` : ''}
          ${gameMode === 'sequence' && sequenceTimes?.length ? 
            `<div style="color: #ffd700; font-size: 16px;">${sequenceTimes.length} targets hit</div>` : ''}
        </div>
        
        <div style="text-align: center; color: #a0a0a0; font-size: 14px;">
          <p style="margin: 0;">Test your reaction time on the blockchain</p>
          <p style="margin: 5px 0 0 0;">#IrysReflex #ReactionTime</p>
        </div>
      `;

      document.body.appendChild(captureElement);

      // Capture the screenshot
      const canvas = await html2canvas(captureElement, {
        backgroundColor: null,
        scale: 2,
        useCORS: true,
        allowTaint: true,
        width: 600,
        height: 400
      });

      document.body.removeChild(captureElement);

      // Convert to blob
      const blob = await new Promise(resolve => canvas.toBlob(resolve, 'image/png', 0.9));
      
      // Upload screenshot to backend
      const formData = new FormData();
      formData.append('screenshot', blob, 'irys-reflex-result.png');
      formData.append('username', username);
      formData.append('gameMode', gameMode);
      formData.append('reactionTime', reactionTime.toString());

      const uploadResponse = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/upload-screenshot`, {
        method: 'POST',
        body: formData
      });

      if (!uploadResponse.ok) {
        throw new Error('Failed to upload screenshot');
      }

      const { imageUrl } = await uploadResponse.json();

      // Create Twitter share URL with text and image
      const shareText = getShareText();
      const twitterUrl = `https://twitter.com/intent/tweet?text=${encodeURIComponent(shareText)}&url=${encodeURIComponent(imageUrl)}`;
      
      // Open Twitter in a new window
      window.open(twitterUrl, '_blank', 'width=550,height=420');
      
      toast.success('🐦 Opening Twitter to share your results!');
      
    } catch (error) {
      console.error('Error sharing to Twitter:', error);
      
      // Fallback: share without image
      const shareText = getShareText();
      const twitterUrl = `https://twitter.com/intent/tweet?text=${encodeURIComponent(shareText)}`;
      window.open(twitterUrl, '_blank', 'width=550,height=420');
      
      toast.error('Screenshot failed, sharing text only');
    } finally {
      setIsSharing(false);
    }
  };

  return (
    <button 
      onClick={captureAndShare}
      disabled={isSharing}
      className="twitter-share-btn"
      title="Share your results on Twitter"
    >
      {isSharing ? (
        <>
          <span>📸</span>
          <span>Capturing...</span>
        </>
      ) : (
        <>
          <span>🐦</span>
          <span>Share on Twitter</span>
        </>
      )}
    </button>
  );
};

export default TwitterShare;