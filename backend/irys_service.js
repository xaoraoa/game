#!/usr/bin/env node

/**
 * Irys Service Helper - Node.js
 * Based on working Notion-Web3 pattern
 * This handles all Irys SDK operations and communicates with Python via JSON
 */

const { Uploader } = require("@irys/upload");
const { Ethereum } = require("@irys/upload-ethereum");
require('dotenv').config();

class IrysService {
    constructor() {
        this.uploader = null;
        this.account = null;
        this.initialized = false;
    }

    async initialize() {
        try {
            const privateKey = process.env.IRYS_PRIVATE_KEY;
            if (!privateKey) {
                throw new Error('IRYS_PRIVATE_KEY not found in environment');
            }

            console.log('Initializing Irys uploader...');
            
            // Initialize uploader with devnet configuration
            this.uploader = await Uploader(Ethereum)
                .withWallet(privateKey)
                .devnet(); // Force devnet for free uploads

            console.log('✅ Irys uploader initialized successfully');
            console.log(`Network: devnet (free uploads)`);
            console.log(`Gateway: https://devnet.irys.xyz`);
            
            this.initialized = true;
            return { success: true, message: 'Irys service initialized' };
        } catch (error) {
            console.error('❌ Failed to initialize Irys:', error.message);
            return { success: false, error: error.message };
        }
    }

    async upload(data, tags = []) {
        try {
            if (!this.initialized) {
                const initResult = await this.initialize();
                if (!initResult.success) {
                    throw new Error(initResult.error);
                }
            }

            console.log('Uploading to Irys devnet...');
            
            // Add default tags
            const allTags = [
                { name: "App-Name", value: "IrysReflex" },
                { name: "Content-Type", value: "application/json" },
                { name: "Timestamp", value: Date.now().toString() },
                ...tags
            ];

            const receipt = await this.uploader.upload(JSON.stringify(data), { tags: allTags });
            
            console.log(`✅ Upload successful: ${receipt.id}`);
            
            return {
                success: true,
                tx_id: receipt.id,
                gateway_url: `https://devnet.irys.xyz/${receipt.id}`,
                explorer_url: `https://devnet.irys.xyz/${receipt.id}`,
                timestamp: receipt.timestamp,
                tags: allTags,
                network: 'devnet',
                verified: true
            };
        } catch (error) {
            console.error('❌ Upload failed:', error.message);
            return {
                success: false,
                error: error.message,
                network: 'devnet'
            };
        }
    }

    async getBalance() {
        try {
            if (!this.initialized) {
                await this.initialize();
            }

            // On devnet, uploads are free, so balance check is not critical
            return {
                success: true,
                balance: 'unlimited (devnet)',
                network: 'devnet',
                message: 'Devnet provides free uploads'
            };
        } catch (error) {
            return {
                success: false,
                error: error.message,
                balance: 0
            };
        }
    }

    async getAddress() {
        try {
            if (!this.initialized) {
                await this.initialize();
            }

            const address = this.uploader.address;
            return {
                success: true,
                address: address,
                network: 'devnet'
            };
        } catch (error) {
            return {
                success: false,
                error: error.message
            };
        }
    }
}

// Main execution
async function main() {
    const service = new IrysService();
    
    // Handle JSON input from Python
    process.stdin.setEncoding('utf8');
    
    let inputData = '';
    process.stdin.on('data', (chunk) => {
        inputData += chunk;
    });

    process.stdin.on('end', async () => {
        try {
            const request = JSON.parse(inputData);
            let response;

            switch (request.action) {
                case 'initialize':
                    response = await service.initialize();
                    break;
                case 'upload':
                    response = await service.upload(request.data, request.tags || []);
                    break;
                case 'balance':
                    response = await service.getBalance();
                    break;
                case 'address':
                    response = await service.getAddress();
                    break;
                default:
                    response = { success: false, error: 'Unknown action' };
            }

            console.log(JSON.stringify(response));
        } catch (error) {
            console.log(JSON.stringify({
                success: false,
                error: error.message
            }));
        }
    });
}

if (require.main === module) {
    main();
}

module.exports = IrysService;