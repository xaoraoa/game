// Keep-alive utility to prevent Render dyno sleep
// Based on working Notion-Web3 pattern

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

export const initKeepAlive = () => {
  if (!BACKEND_URL) {
    console.warn('REACT_APP_BACKEND_URL not set - keep-alive disabled');
    return;
  }

  // Ping the health endpoint every 60 seconds to keep the dyno awake
  const keepAliveInterval = setInterval(() => {
    fetch(`${BACKEND_URL}/api/health`)
      .then(response => {
        if (response.ok) {
          console.log('✅ Keep-alive ping successful');
        } else {
          console.warn('⚠️ Keep-alive ping failed:', response.status);
        }
      })
      .catch(error => {
        console.warn('⚠️ Keep-alive ping error:', error.message);
      });
  }, 60000); // 60 seconds

  console.log('🔄 Keep-alive service started (60s interval)');
  
  // Return cleanup function
  return () => {
    clearInterval(keepAliveInterval);
    console.log('🛑 Keep-alive service stopped');
  };
};