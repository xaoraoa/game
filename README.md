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
│   ├── index.py      # exports handler = Mangum(app)
│   └── requirements.txt
├── render.yaml       # Render.com deployment config
├── vercel.json       # Vercel deployment config
├── .env.render       # Environment variables for Render
└── deploy-render.sh  # Deployment helper script
```
