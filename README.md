# Irys Reflex - Reaction Time Tester 🎯

> Test your reaction time on the blockchain with Irys Reflex - A modern, decentralized reaction time testing game.

## 🚀 Quick Start

**Irys Reflex** is a blockchain-powered reaction time tester featuring multiple game modes, permanent score storage on Irys blockchain, and competitive leaderboards.

### Features
- 🎮 **4 Game Modes**: Classic, Sequence, Endurance, Precision
- ⛓️ **Blockchain Storage**: Permanent score storage on Irys network
- 🔗 **Wallet Integration**: MetaMask connection for score verification
- 🏆 **Global Leaderboard**: Compete with players worldwide
- 🎨 **Beautiful UI**: Irys-themed design with glassmorphism effects
- 📱 **Responsive**: Works on desktop, tablet, and mobile

### Game Modes
- **Classic (🎯)**: Traditional single-target reaction time test
- **Sequence (🔄)**: Hit multiple targets in sequence
- **Endurance (⏱️)**: Hit as many targets as possible in 60 seconds  
- **Precision (🎪)**: Smaller targets for accuracy testing

### Tech Stack
- **Frontend**: React.js + TailwindCSS
- **Backend**: FastAPI + MongoDB
- **Blockchain**: Irys Network (Arweave)
- **Wallet**: MetaMask Integration

## 🎮 How to Play

1. **Connect Wallet**: Link your MetaMask wallet
2. **Choose Mode**: Select your preferred game mode
3. **Enter Username**: Provide a display name
4. **Play**: Click the circle when it flashes Irys cyan
5. **Save Score**: Store your results on blockchain

## 🏗️ Development

### Prerequisites
- Node.js 18+
- Python 3.8+
- MongoDB
- MetaMask wallet

### Installation
```bash
# Clone repository
git clone <repository-url>
cd irys-reflex

# Install backend dependencies
cd backend
pip install -r requirements.txt

# Install frontend dependencies  
cd ../frontend
yarn install

# Start development servers
yarn start  # Frontend
python server.py  # Backend
```

### Environment Variables
```bash
# Backend (.env)
MONGO_URL=mongodb://localhost:27017
IRYS_PRIVATE_KEY=your_private_key
IRYS_NETWORK=testnet

# Frontend (.env)
REACT_APP_BACKEND_URL=http://localhost:8001
```

## 📊 Deployment

Ready for deployment on:
- **Render.com** (Primary)
- **Vercel** (Frontend)
- **Railway** (Backend)

## 🔗 Links

- 📖 [Full Documentation](./IRYS_REFLEX_DOCUMENTATION.md)
- 🌐 [Irys Network](https://irys.xyz)
- 🦊 [MetaMask](https://metamask.io)
- 🔍 [Irys Explorer](https://testnet.irys.xyz)

---

*Built with ❤️ for the decentralized web*
