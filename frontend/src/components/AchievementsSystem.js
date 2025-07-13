import React, { useState, useEffect } from 'react';
import toast from 'react-hot-toast';

const AchievementsSystem = ({ playerAddress, gameStats }) => {
  const [achievements, setAchievements] = useState([]);
  const [availableAchievements, setAvailableAchievements] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (playerAddress) {
      loadAchievements();
      loadAvailableAchievements();
    }
  }, [playerAddress]);

  useEffect(() => {
    if (gameStats && playerAddress) {
      checkForNewAchievements();
    }
  }, [gameStats, playerAddress]);

  const loadAchievements = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/achievements/${playerAddress}`);
      const data = await response.json();
      setAchievements(data.achievements || []);
    } catch (error) {
      console.error('Error loading achievements:', error);
    }
  };

  const loadAvailableAchievements = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/achievements/types`);
      const data = await response.json();
      setAvailableAchievements(data.types || []);
    } catch (error) {
      console.error('Error loading available achievements:', error);
    }
  };

  const checkForNewAchievements = async () => {
    if (!gameStats || !playerAddress) return;

    const unlockedTypes = Array.isArray(achievements) ? achievements.map(a => a.achievement_type) : [];
    const toCheck = Array.isArray(availableAchievements) ? availableAchievements.filter(a => !unlockedTypes.includes(a.id)) : [];

    for (const achievement of toCheck) {
      if (shouldUnlockAchievement(achievement, gameStats)) {
        await unlockAchievement(achievement);
      }
    }
  };

  const shouldUnlockAchievement = (achievement, stats) => {
    switch (achievement.id) {
      case 'speed_demon':
        return stats.lastTime && stats.lastTime < 200 && !stats.lastPenalty;
      
      case 'consistency_master':
        // Check if last 10 games have variance < 50ms
        return stats.recentGames && stats.recentGames.length >= 10 && 
               calculateVariance(stats.recentGames.slice(-10)) < 50;
      
      case 'endurance_champion':
        return stats.lastGameMode === 'endurance' && stats.lastHits >= 50;
      
      case 'precision_master':
        return stats.lastGameMode === 'precision' && stats.lastAccuracy >= 95;
      
      case 'sequence_pro':
        return stats.lastGameMode === 'sequence' && stats.lastTargets >= 10;
      
      case 'streak_legend':
        return stats.dailyStreak >= 7;
      
      default:
        return false;
    }
  };

  const calculateVariance = (times) => {
    if (times.length < 2) return 0;
    
    const mean = times.reduce((sum, time) => sum + time, 0) / times.length;
    const variance = times.reduce((sum, time) => sum + Math.pow(time - mean, 2), 0) / times.length;
    return Math.sqrt(variance);
  };

  const unlockAchievement = async (achievementType) => {
    try {
      setLoading(true);
      
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/achievements/unlock`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          player: playerAddress,
          achievement_type: achievementType.id,
          title: achievementType.title,
          description: achievementType.description,
          icon: achievementType.icon
        })
      });

      const result = await response.json();
      
      if (result.status === 'unlocked') {
        setAchievements(prev => [...prev, result.achievement]);
        
        // Show celebration toast
        toast.success(
          <div className="achievement-toast">
            <span className="achievement-icon">{achievementType.icon}</span>
            <div>
              <div className="achievement-title">Achievement Unlocked!</div>
              <div className="achievement-desc">{achievementType.title}</div>
            </div>
          </div>,
          {
            duration: 5000,
            position: 'top-center',
            style: {
              background: 'linear-gradient(135deg, #00FFD1 0%, #3A007A 100%)',
              color: 'white',
              fontWeight: 'bold',
              borderRadius: '15px',
              padding: '15px'
            }
          }
        );
      }
    } catch (error) {
      console.error('Error unlocking achievement:', error);
      toast.error('Failed to unlock achievement');
    } finally {
      setLoading(false);
    }
  };

  const AchievementCard = ({ achievement, isUnlocked }) => (
    <div className={`achievement-card ${isUnlocked ? 'unlocked' : 'locked'}`}>
      <div className="achievement-icon-large">
        {isUnlocked ? achievement.icon : '🔒'}
      </div>
      <div className="achievement-details">
        <h3 className="achievement-title">
          {isUnlocked ? achievement.title : '???'}
        </h3>
        <p className="achievement-description">
          {isUnlocked ? achievement.description : 'Keep playing to unlock!'}
        </p>
        {isUnlocked && achievement.unlocked_at && (
          <div className="achievement-date">
            Unlocked: {new Date(achievement.unlocked_at).toLocaleDateString()}
          </div>
        )}
        {isUnlocked && achievement.verified && (
          <div className="achievement-verified">
            <span className="verified-icon">✅</span>
            Verified on blockchain
          </div>
        )}
      </div>
    </div>
  );

  return (
    <div className="achievements-system">
      <h2 className="achievements-title">
        <span className="title-icon">🏆</span>
        Achievements
        <span className="achievement-count">
          {achievements.length}/{availableAchievements.length}
        </span>
      </h2>
      
      <div className="achievements-grid">
        {availableAchievements.map(availableAchievement => {
          const unlockedAchievement = achievements.find(
            a => a.achievement_type === availableAchievement.id
          );
          
          return (
            <AchievementCard
              key={availableAchievement.id}
              achievement={unlockedAchievement || availableAchievement}
              isUnlocked={!!unlockedAchievement}
            />
          );
        })}
      </div>
      
      {loading && (
        <div className="loading-overlay">
          <div className="spinner"></div>
          <p>Checking achievements...</p>
        </div>
      )}
    </div>
  );
};

export default AchievementsSystem;