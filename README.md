# Irys Reflex - Reaction Time Tester

A high-performance reaction time testing game built with React, FastAPI, and blockchain integration using the Irys SDK. Test your reflexes and store your scores permanently on-chain!

## 🚀 Features

- **Reaction Time Testing**: Multiple game modes including Classic, Sequence, Endurance, and Precision
- **Blockchain Integration**: Scores stored permanently using Irys Protocol
- **Real-time Leaderboards**: Global and personal statistics
- **Modern UI**: Glassmorphism design with Irys branding
- **Wallet Integration**: MetaMask connection for blockchain transactions
- **Fake-start Penalty**: Advanced timing detection system

## 🏗️ Architecture

- **Frontend**: React 18 with TailwindCSS and Create React App
- **Backend**: FastAPI with MongoDB
- **Blockchain**: Irys Protocol for permanent data storage
- **Deployment**: Ready for Render.com, Vercel, or local development

## 📦 Project Structure

```
/
├── frontend/         # React/CRA game client
│   ├── public/
│   │   └── _redirects    # "/* /index.html 200"
│   ├── src/
│   │   ├── App.js
│   │   ├── components/
│   │   └── lib/irys.js
│   ├── package.json
│   └── craco.config.js
├── backend/          # FastAPI + Mangum
│   ├── server.py
## 🚀 Deploy to Render.com

### Quick Deploy (Recommended)

1. **Install Render CLI**:
   ```bash
   # macOS
   brew install render-cli
   
   # npm
   npm install -g @render/cli
   
   # Or download from https://render.com/docs/cli
   ```

2. **Login to Render**:
   ```bash
   render auth login
   ```

3. **Run the deployment script**:
   ```bash
   ./deploy-render.sh
   ```

4. **Configure environment variables** in the Render Dashboard (see [Environment Setup](#environment-setup) below)

### Manual Deploy

1. **Fork/Clone this repository**

2. **Connect to Render**:
   - Go to [Render Dashboard](https://dashboard.render.com)
   - Click "New" → "Blueprint"
   - Connect your GitHub repository
   - Render will automatically detect the `render.yaml` file

3. **Configure Environment Variables** (see section below)

4. **Deploy**: Click "Apply" to start the deployment

### Environment Setup

#### Frontend Environment Variables
Set these in **Render Dashboard** → **irys-reflex-frontend** → **Environment**:

```bash
REACT_APP_PRIVATE_KEY=your_private_key_here
```

The following are automatically configured in `render.yaml`:
- `REACT_APP_BACKEND_URL` → Points to your backend service
- `REACT_APP_IRYS_RPC_URL` → Irys devnet RPC
- `REACT_APP_GATEWAY_URL` → Irys devnet gateway

#### Backend Environment Variables
Set these in **Render Dashboard** → **irys-reflex-backend** → **Environment**:

```bash
MONGO_URL=mongodb+srv://username:password@cluster.mongodb.net/irys_reflex_prod?retryWrites=true&w=majority
```

#### MongoDB Atlas Setup

1. **Create Free Cluster**:
   - Go to [MongoDB Atlas](https://cloud.mongodb.com)
   - Create a free M0 cluster
   - Choose a cloud provider and region

2. **Database Access**:
   - Create a database user
   - Note the username and password

3. **Network Access**:
   - Add IP address `0.0.0.0/0` (all IPs) for development
   - For production, restrict to Render's IP ranges

4. **Get Connection String**:
   - Click "Connect" → "Connect your application"
   - Copy the connection string
   - Replace `<password>` with your database user password

#### Irys Configuration

1. **Get a Wallet**:
   - Install MetaMask or similar wallet
   - Create/import a wallet

2. **Get Testnet ETH**:
   - Switch to Arbitrum Sepolia testnet
   - Get testnet ETH from faucet

3. **Export Private Key**:
   - In MetaMask: Account menu → Account details → Export private key
   - ⚠️ **Security**: Only use testnet keys, never mainnet!

### Verification

After deployment completes:

- **Frontend**: Visit `https://irys-reflex-frontend.onrender.com`
- **Backend API**: Visit `https://irys-reflex-backend.onrender.com/api/health`
- **Game**: Connect wallet and test reaction time!

### Deployment Commands

```bash
# Deploy using Blueprint (render.yaml)
render services create --apply render.yaml

# Update existing services
render services update --apply render.yaml

# Check service status
render services list

# View service logs
render services logs irys-reflex-frontend
render services logs irys-reflex-backend
```

## 🛠️ Local Development

### Prerequisites

- Node.js 18+ and Yarn
- Python 3.11+
- MongoDB (local or Atlas)

### Setup

1. **Clone the repository**:
   ```bash
   git clone <your-repo-url>
   cd irys-reflex
   ```

2. **Install dependencies**:
   ```bash
   # Frontend
   cd frontend
   yarn install
   
   # Backend
   cd ../backend
   pip install -r requirements.txt
   ```

3. **Environment setup**:
   ```bash
   # Copy environment templates
   cp .env.example frontend/.env
   cp .env.example backend/.env
   
   # Edit the .env files with your configuration
   ```

4. **Start services**:
   ```bash
   # Start backend (terminal 1)
   cd backend
   uvicorn server:app --reload --host 0.0.0.0 --port 8001
   
   # Start frontend (terminal 2)
   cd frontend
   yarn start
   ```

5. **Access the app**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8001/api/health

## 🎮 Game Modes

- **Classic**: Single target reaction test
- **Sequence**: Multiple targets in sequence
- **Endurance**: Continuous targets for stamina
- **Precision**: Accuracy-focused challenges

## 🏆 Leaderboards

Global and personal statistics are automatically tracked and stored on-chain via Irys Protocol, ensuring permanent and tamper-proof records.

## 🔧 API Endpoints

- `GET /api/health` - Health check
- `GET /api/game-modes` - Available game modes
- `POST /api/scores` - Submit score
- `GET /api/leaderboard` - Global leaderboard
- `GET /api/player/{address}` - Player statistics

## 📊 Tech Stack

- **Frontend**: React 18, TailwindCSS, Irys SDK, Ethers.js
- **Backend**: FastAPI, MongoDB, Motor (async MongoDB)
- **Blockchain**: Irys Protocol (Arweave + Ethereum)
- **Deployment**: Render.com, Vercel support
- **Wallet**: MetaMask integration

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🆘 Support

- **Render Issues**: Check [Render Documentation](https://render.com/docs)
- **Irys Integration**: See [Irys Documentation](https://docs.irys.xyz)
- **MongoDB**: Check [MongoDB Atlas Documentation](https://docs.atlas.mongodb.com)

---

**Made with ❤️ using Irys Protocol for permanent data storage**
│   ├── index.py      # exports handler = Mangum(app)
│   └── requirements.txt
├── render.yaml       # Render.com deployment config
├── vercel.json       # Vercel deployment config
├── .env.render       # Environment variables for Render
└── deploy-render.sh  # Deployment helper script
```
