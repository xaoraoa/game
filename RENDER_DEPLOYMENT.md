# 🚀 Render Deployment Quick Reference

## Pre-Deployment Checklist

- [ ] Code pushed to GitHub repository
- [ ] MongoDB Atlas cluster created (free tier)
- [ ] Testnet private key ready for Irys
- [ ] Render account created

## Environment Variables to Set

### Frontend Service (irys-reflex-frontend)
```bash
REACT_APP_PRIVATE_KEY=0x... # Your testnet private key
```

### Backend Service (irys-reflex-backend)  
```bash
MONGO_URL=mongodb+srv://user:pass@cluster.mongodb.net/irys_reflex_prod
```

## Deployment Methods

### 🎯 Option 1: Automated (Recommended)
```bash
./deploy-render.sh
```

### 🛠️ Option 2: Manual Dashboard
1. Go to [render.com/dashboard](https://dashboard.render.com)
2. New → Blueprint
3. Connect GitHub repo
4. Apply render.yaml

### 🖥️ Option 3: CLI Manual
```bash
render auth login
render services create --apply render.yaml
```

## Service URLs (After Deployment)

- **Frontend**: https://irys-reflex-frontend.onrender.com
- **Backend**: https://irys-reflex-backend.onrender.com
- **Health Check**: https://irys-reflex-backend.onrender.com/api/health

## Common Commands

```bash
# Check validation
./validate-render.sh

# View service status
render services list

# View logs
render services logs irys-reflex-frontend
render services logs irys-reflex-backend

# Update services
render services update --apply render.yaml
```

## MongoDB Atlas Setup

1. **Create Cluster**: [cloud.mongodb.com](https://cloud.mongodb.com)
2. **Database Access**: Create user with read/write access
3. **Network Access**: Add IP `0.0.0.0/0` (all IPs)
4. **Connection**: Get connection string from "Connect" button

## Troubleshooting

### Build Fails
- Check environment variables are set
- Verify all dependencies in package.json/requirements.txt
- Check build logs in Render dashboard

### Frontend Not Loading
- Verify `_redirects` file exists for SPA routing
- Check static site is published from correct directory (`frontend/build`)

### Backend Health Check Fails
- Verify MongoDB connection string
- Check `/api/health` endpoint manually
- Review backend logs for errors

### CORS Issues
- Backend allows all origins by default
- Verify frontend is calling correct backend URL

## 🆘 Support Links

- [Render Docs](https://render.com/docs)
- [MongoDB Atlas Docs](https://docs.atlas.mongodb.com)
- [Irys SDK Docs](https://docs.irys.xyz)

---
**Deployment Time**: ~5-10 minutes  
**Free Tier**: ✅ Supported  
**Auto-Deploy**: ✅ On git push