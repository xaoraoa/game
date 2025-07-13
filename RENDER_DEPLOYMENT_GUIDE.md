# Render Deployment Instructions for Irys Reflex

## 🚀 Step-by-Step Render Deployment Guide

### Phase 1: Pre-Deployment Setup

1. **Create a GitHub Repository**
   - Push your entire `/app` folder to a GitHub repository
   - Make sure all files are committed including `render.yaml`

2. **Get Required API Keys**
   - **MongoDB Atlas**: Create a free cluster at mongodb.com/atlas
     - Get connection string: `mongodb+srv://username:password@cluster.mongodb.net/`
   - **Irys Private Key**: Use your existing key or generate a new one
     - Current key: `725bbe9ad10ef6b48397d37501ff0c908119fdc0513a85a046884fc9157c80f5`

### Phase 2: Render Setup

1. **Connect to Render**
   - Go to render.com
   - Sign in with GitHub
   - Click "New" → "Blueprint"
   - Connect your GitHub repository

2. **Configure Environment Variables**

   **For Backend Service (irys-reflex-backend):**
   ```
   MONGO_URL = mongodb+srv://your-username:your-password@your-cluster.mongodb.net/
   DB_NAME = irys_reflex_prod
   IRYS_PRIVATE_KEY = 725bbe9ad10ef6b48397d37501ff0c908119fdc0513a85a046884fc9157c80f5
   IRYS_NETWORK = testnet
   ENVIRONMENT = production
   ```

   **For Frontend Service (irys-reflex-frontend):**
   ```
   REACT_APP_BACKEND_URL = https://irys-reflex-backend.onrender.com
   REACT_APP_IRYS_RPC_URL = https://rpc.devnet.irys.xyz/v1
   REACT_APP_GATEWAY_URL = https://devnet.irys.xyz
   REACT_APP_PRIVATE_KEY = [Set manually if needed for frontend wallet operations]
   ```

### Phase 3: Deploy

1. **Deploy via Blueprint**
   - Render will read your `render.yaml` file
   - Both frontend and backend will deploy automatically
   - Monitor logs for any issues

2. **Verify Deployment**
   - Backend health check: `https://irys-reflex-backend.onrender.com/api/health`
   - Frontend: `https://irys-reflex-frontend.onrender.com`

### Phase 4: Troubleshooting Common Issues

#### CORS Errors
✅ **FIXED**: Backend now includes specific origin configuration:
- `https://irys-reflex-frontend.onrender.com`
- Proper CORS headers and OPTIONS handler

#### Network Timeouts
- **Solution**: Add keep-alive endpoint (already implemented as `/api/health`)
- **Note**: Free tier services sleep after inactivity

#### Build Failures
- **Frontend**: Check Node.js memory (set to 8GB in render.yaml)
- **Backend**: Ensure all requirements are in requirements.txt
- **Python 3.13 Issues**: Fixed with setuptools>=65.0.0 and runtime: python-3.11
- **Missing pkg_resources**: Fixed by adding setuptools to requirements.txt

#### Database Connection
- **Error**: "MongoServerError: bad auth"
- **Solution**: Check MongoDB Atlas IP whitelist (add 0.0.0.0/0 for all IPs)

### Phase 5: Performance Optimization

1. **Keep Services Warm**
   ```javascript
   // Add to frontend (optional)
   setInterval(() => {
     fetch(`${process.env.REACT_APP_BACKEND_URL}/api/health`).catch(() => {});
   }, 840000); // 14 minutes
   ```

2. **Monitor Logs**
   - Backend: Check Render dashboard logs
   - Frontend: Browser console for client errors

### Phase 6: Post-Deployment Testing

1. **Functional Tests**
   - [ ] Frontend loads without CORS errors
   - [ ] Wallet connection works (MetaMask)
   - [ ] Game modes are fetched from backend
   - [ ] Score submission to Irys blockchain
   - [ ] Leaderboard displays correctly

2. **Performance Tests**
   - [ ] First load time < 5 seconds
   - [ ] Game interactions are responsive
   - [ ] No JavaScript errors in console

## 🔧 Configuration Files Status

- ✅ `render.yaml` - Deployment configuration ready
- ✅ `backend/server.py` - CORS fixed for Render
- ✅ `frontend/.env` - Updated for Render backend URL
- ✅ `backend/requirements.txt` - All dependencies listed
- ✅ Health check endpoint configured

## 🚨 Important Notes

1. **Free Tier Limitations**
   - Services sleep after 15 minutes of inactivity
   - Cold starts take 30-60 seconds
   - 750 hours/month limit per service

2. **Security**
   - Private keys are secure in Render environment variables
   - Never commit private keys to Git

3. **Backup Plan**
   - If CORS issues persist, try adding your specific domain to origins
   - Monitor browser developer tools for specific error messages

## ✅ Deployment Checklist

- [ ] GitHub repository created and pushed
- [ ] MongoDB Atlas cluster created
- [ ] Render Blueprint deployed
- [ ] Environment variables configured
- [ ] Health check endpoint accessible
- [ ] Frontend loads without CORS errors
- [ ] Game functionality works end-to-end
- [ ] Irys blockchain integration working

Your app is now ready for Render deployment! 🎉