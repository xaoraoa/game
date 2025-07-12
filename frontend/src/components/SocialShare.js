import React, { useState, useRef } from 'react';
import html2canvas from 'html2canvas';
import toast from 'react-hot-toast';

const SocialShare = ({ playerAddress, playerStats }) => {
  const [isGenerating, setIsGenerating] = useState(false);
  const statsCardRef = useRef(null);

  const generateStatsCard = async () => {
    if (!playerStats || !playerAddress) return;

    setIsGenerating(true);
    try {
      // Generate screenshot of stats card
      const canvas = await html2canvas(statsCardRef.current, {
        backgroundColor: '#0A0A0A',
        width: 800,
        height: 600,
        scale: 2,
        logging: false,
        useCORS: true
      });

      // Convert to blob
      const blob = await new Promise(resolve => {
        canvas.toBlob(resolve, 'image/png', 0.9);
      });

      // Create stats text
      const statsText = `🎯 My Irys Reflex Stats:
⚡ Best Time: ${playerStats.best_time}ms
🎮 Total Games: ${playerStats.total_games}
🏆 Achievements: ${playerStats.total_achievements}
📈 Average: ${playerStats.average_time}ms

Play now at IrysReflex.com!
#IrysReflex #ReactionTime #Gaming #Blockchain`;

      // Share to Twitter/X
      await shareToTwitter(statsText, blob);
      
    } catch (error) {
      console.error('Error generating stats card:', error);
      toast.error('Failed to generate stats card');
    } finally {
      setIsGenerating(false);
    }
  };

  const shareToTwitter = async (text, imageBlob) => {
    try {
      // For now, we'll use the Twitter Web Intent API
      // In a real app, you might use Twitter API v2 with proper authentication
      
      const encodedText = encodeURIComponent(text);
      const twitterUrl = `https://twitter.com/intent/tweet?text=${encodedText}`;
      
      // Open Twitter in new window
      window.open(twitterUrl, '_blank', 'width=600,height=400');
      
      // Show success message
      toast.success('Opening Twitter to share your stats!');
      
    } catch (error) {
      console.error('Error sharing to Twitter:', error);
      toast.error('Failed to share to Twitter');
    }
  };

  const copyStatsToClipboard = () => {
    if (!playerStats) return;

    const statsText = `🎯 My Irys Reflex Stats:
⚡ Best Time: ${playerStats.best_time}ms
🎮 Total Games: ${playerStats.total_games}
🏆 Achievements: ${playerStats.total_achievements}
📈 Average: ${playerStats.average_time}ms

Play now at IrysReflex.com!`;

    navigator.clipboard.writeText(statsText).then(() => {
      toast.success('Stats copied to clipboard!');
    }).catch((error) => {
      console.error('Error copying to clipboard:', error);
      toast.error('Failed to copy stats');
    });
  };

  if (!playerStats || !playerAddress) {
    return (
      <div className="social-share-empty">
        <p>Connect your wallet and play some games to unlock social sharing!</p>
      </div>
    );
  }

  return (
    <div className="social-share">
      <div className="share-header">
        <h3>Share Your Stats</h3>
        <p>Show off your reaction time skills!</p>
      </div>

      {/* Stats Card for Screenshot */}
      <div 
        ref={statsCardRef} 
        className="stats-card-screenshot"
        style={{ 
          position: 'absolute', 
          left: '-9999px', 
          width: '800px', 
          height: '600px',
          background: 'linear-gradient(135deg, #0A0A0A 0%, #1A1A1A 100%)',
          color: 'white',
          padding: '60px',
          borderRadius: '20px',
          fontFamily: 'Inter, sans-serif'
        }}
      >
        <div style={{ textAlign: 'center' }}>
          <h1 style={{ 
            fontSize: '48px', 
            marginBottom: '20px',
            background: 'linear-gradient(135deg, #00FFD1 0%, #3A007A 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            fontWeight: 'bold'
          }}>
            Irys Reflex
          </h1>
          
          <div style={{ 
            fontSize: '32px', 
            marginBottom: '40px',
            opacity: 0.8 
          }}>
            Player Stats
          </div>
          
          <div style={{ 
            display: 'grid', 
            gridTemplateColumns: '1fr 1fr',
            gap: '40px',
            marginBottom: '40px'
          }}>
            <div>
              <div style={{ fontSize: '18px', opacity: 0.7 }}>Best Time</div>
              <div style={{ fontSize: '36px', fontWeight: 'bold', color: '#00FFD1' }}>
                {playerStats.best_time}ms
              </div>
            </div>
            <div>
              <div style={{ fontSize: '18px', opacity: 0.7 }}>Total Games</div>
              <div style={{ fontSize: '36px', fontWeight: 'bold', color: '#00FFD1' }}>
                {playerStats.total_games}
              </div>
            </div>
            <div>
              <div style={{ fontSize: '18px', opacity: 0.7 }}>Achievements</div>
              <div style={{ fontSize: '36px', fontWeight: 'bold', color: '#00FFD1' }}>
                {playerStats.total_achievements}
              </div>
            </div>
            <div>
              <div style={{ fontSize: '18px', opacity: 0.7 }}>Average</div>
              <div style={{ fontSize: '36px', fontWeight: 'bold', color: '#00FFD1' }}>
                {playerStats.average_time}ms
              </div>
            </div>
          </div>
          
          <div style={{ 
            opacity: 0.6, 
            fontSize: '20px' 
          }}>
            Play at IrysReflex.com
          </div>
        </div>
      </div>

      {/* Share Buttons */}
      <div className="share-buttons">
        <button
          onClick={generateStatsCard}
          disabled={isGenerating}
          className="share-btn twitter-share"
        >
          {isGenerating ? (
            <>
              <div className="spinner"></div>
              Generating...
            </>
          ) : (
            <>
              <span className="share-icon">𝕏</span>
              Share on X/Twitter
            </>
          )}
        </button>
        
        <button
          onClick={copyStatsToClipboard}
          className="share-btn copy-stats"
        >
          <span className="share-icon">📋</span>
          Copy Stats
        </button>
      </div>

      {/* Preview Card */}
      <div className="stats-preview">
        <h4>Stats Preview</h4>
        <div className="preview-card">
          <div className="preview-header">
            <span className="preview-icon">🎯</span>
            <span>Irys Reflex Stats</span>
          </div>
          <div className="preview-stats">
            <div className="stat-item">
              <span className="stat-label">Best Time:</span>
              <span className="stat-value">{playerStats.best_time}ms</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Total Games:</span>
              <span className="stat-value">{playerStats.total_games}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Achievements:</span>
              <span className="stat-value">{playerStats.total_achievements}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Average:</span>
              <span className="stat-value">{playerStats.average_time}ms</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SocialShare;