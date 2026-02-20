#!/usr/bin/env node
/**
 * Social Media MCP Server (Gold Tier)
 * ====================================
 * Node.js + Express MCP server for social media posting
 * 
 * Endpoints:
 * - POST /post-fb  - Post to Facebook
 * - POST /post-ig  - Post to Instagram
 * - POST /post-x   - Post to Twitter/X
 * - POST /post-all - Post to all platforms
 * - GET  /health   - Health check
 * 
 * Uses Playwright internally via child_process
 * Credentials from .env file
 */

const express = require('express');
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');
require('dotenv').config();

const app = express();
const PORT = process.env.MCP_PORT || 3000;

// Middleware
app.use(express.json());

// Base directory (same as scripts)
const BASE_DIR = __dirname;
const SCRIPTS_DIR = BASE_DIR;

// Environment credentials
const CREDENTIALS = {
    facebook: {
        email: process.env.FB_EMAIL || '',
        password: process.env.FB_PASSWORD || ''
    },
    instagram: {
        username: process.env.IG_USERNAME || '',
        password: process.env.IG_PASSWORD || ''
    },
    twitter: {
        email: process.env.TWITTER_EMAIL || '',
        password: process.env.TWITTER_PASSWORD || ''
    }
};

/**
 * Run a Python script via subprocess
 * @param {string} script - Script name
 * @param {Array} args - Command line arguments
 * @returns {Promise<{success: boolean, output: string}>}
 */
function runPythonScript(script, args = []) {
    return new Promise((resolve, reject) => {
        const scriptPath = path.join(SCRIPTS_DIR, script);
        
        if (!fs.existsSync(scriptPath)) {
            reject(new Error(`Script not found: ${scriptPath}`));
            return;
        }

        const pythonArgs = [scriptPath, ...args];
        const env = {
            ...process.env,
            PYTHONUNBUFFERED: '1'
        };

        console.log(`Running: python ${pythonArgs.join(' ')}`);

        const child = spawn('python3', pythonArgs, {
            cwd: BASE_DIR,
            env: env,
            stdio: ['pipe', 'pipe', 'pipe']
        });

        let stdout = '';
        let stderr = '';

        child.stdout.on('data', (data) => {
            const text = data.toString();
            stdout += text;
            console.log(`[stdout] ${text}`);
        });

        child.stderr.on('data', (data) => {
            const text = data.toString();
            stderr += text;
            console.error(`[stderr] ${text}`);
        });

        child.on('close', (code) => {
            if (code === 0) {
                resolve({ success: true, output: stdout, code });
            } else {
                resolve({ success: false, output: stderr || stdout, code });
            }
        });

        child.on('error', (err) => {
            reject(err);
        });
    });
}

/**
 * Validate credentials for a platform
 * @param {string} platform - Platform name
 * @returns {boolean}
 */
function validateCredentials(platform) {
    const creds = CREDENTIALS[platform];
    if (!creds) return false;
    
    const values = Object.values(creds);
    return values.every(v => v && v.length > 0);
}

/**
 * Health check endpoint
 */
app.get('/health', (req, res) => {
    res.json({
        status: 'healthy',
        timestamp: new Date().toISOString(),
        version: '1.0.0-gold',
        endpoints: [
            'POST /post-fb',
            'POST /post-ig',
            'POST /post-x',
            'POST /post-all',
            'GET /health'
        ]
    });
});

/**
 * POST /post-fb - Post to Facebook
 * Request body:
 * {
 *   "text": "Post content",
 *   "image": "/path/to/image.jpg" (optional)
 * }
 */
app.post('/post-fb', async (req, res) => {
    console.log('Received POST /post-fb request');
    
    const { text, image } = req.body;

    if (!text) {
        return res.status(400).json({
            success: false,
            error: 'Text is required'
        });
    }

    if (!validateCredentials('facebook')) {
        return res.status(401).json({
            success: false,
            error: 'Facebook credentials not configured (FB_EMAIL, FB_PASSWORD)'
        });
    }

    try {
        const args = [`--text=${text}`];
        if (image) {
            args.push(`--image=${image}`);
        }
        args.push('--platform=fb');

        const result = await runPythonScript('fb_ig_browser_poster.py', args);

        res.json({
            success: result.success,
            platform: 'facebook',
            output: result.output,
            timestamp: new Date().toISOString()
        });
    } catch (error) {
        console.error('Facebook post error:', error);
        res.status(500).json({
            success: false,
            error: error.message
        });
    }
});

/**
 * POST /post-ig - Post to Instagram
 * Request body:
 * {
 *   "text": "Post content (caption)",
 *   "image": "/path/to/image.jpg" (required for IG)
 * }
 */
app.post('/post-ig', async (req, res) => {
    console.log('Received POST /post-ig request');
    
    const { text, image } = req.body;

    if (!text) {
        return res.status(400).json({
            success: false,
            error: 'Text (caption) is required'
        });
    }

    if (!image) {
        return res.status(400).json({
            success: false,
            error: 'Image is required for Instagram posts'
        });
    }

    if (!validateCredentials('instagram')) {
        return res.status(401).json({
            success: false,
            error: 'Instagram credentials not configured (IG_USERNAME, IG_PASSWORD)'
        });
    }

    try {
        const args = [`--text=${text}`, `--image=${image}`, '--platform=ig'];

        const result = await runPythonScript('fb_ig_browser_poster.py', args);

        res.json({
            success: result.success,
            platform: 'instagram',
            output: result.output,
            timestamp: new Date().toISOString()
        });
    } catch (error) {
        console.error('Instagram post error:', error);
        res.status(500).json({
            success: false,
            error: error.message
        });
    }
});

/**
 * POST /post-x - Post to Twitter/X
 * Request body:
 * {
 *   "text": "Tweet content",
 *   "image": "/path/to/image.jpg" (optional)
 * }
 */
app.post('/post-x', async (req, res) => {
    console.log('Received POST /post-x request');
    
    const { text, image } = req.body;

    if (!text) {
        return res.status(400).json({
            success: false,
            error: 'Text is required'
        });
    }

    if (!validateCredentials('twitter')) {
        return res.status(401).json({
            success: false,
            error: 'Twitter credentials not configured (TWITTER_EMAIL, TWITTER_PASSWORD)'
        });
    }

    try {
        const args = [`--text=${text}`];
        if (image) {
            args.push(`--image=${image}`);
        }

        const result = await runPythonScript('twitter_browser_poster.py', args);

        res.json({
            success: result.success,
            platform: 'twitter',
            output: result.output,
            timestamp: new Date().toISOString()
        });
    } catch (error) {
        console.error('Twitter post error:', error);
        res.status(500).json({
            success: false,
            error: error.message
        });
    }
});

/**
 * POST /post-all - Post to all platforms
 * Request body:
 * {
 *   "text": "Post content",
 *   "image": "/path/to/image.jpg" (optional, required for IG)
 * }
 */
app.post('/post-all', async (req, res) => {
    console.log('Received POST /post-all request');
    
    const { text, image } = req.body;

    if (!text) {
        return res.status(400).json({
            success: false,
            error: 'Text is required'
        });
    }

    const results = {
        facebook: null,
        instagram: null,
        twitter: null
    };

    // Post to Facebook
    if (validateCredentials('facebook')) {
        try {
            const args = [`--text=${text}`];
            if (image) args.push(`--image=${image}`);
            args.push('--platform=fb');
            
            results.facebook = await runPythonScript('fb_ig_browser_poster.py', args);
        } catch (error) {
            results.facebook = { success: false, error: error.message };
        }
    }

    // Post to Instagram (only if image provided)
    if (image && validateCredentials('instagram')) {
        try {
            const args = [`--text=${text}`, `--image=${image}`, '--platform=ig'];
            results.instagram = await runPythonScript('fb_ig_browser_poster.py', args);
        } catch (error) {
            results.instagram = { success: false, error: error.message };
        }
    }

    // Post to Twitter
    if (validateCredentials('twitter')) {
        try {
            const args = [`--text=${text}`];
            if (image) args.push(`--image=${image}`);
            results.twitter = await runPythonScript('twitter_browser_poster.py', args);
        } catch (error) {
            results.twitter = { success: false, error: error.message };
        }
    }

    const allSuccess = Object.values(results).every(r => r && r.success);

    res.json({
        success: allSuccess,
        platforms: results,
        timestamp: new Date().toISOString()
    });
});

/**
 * GET /credentials - Check configured credentials (without exposing values)
 */
app.get('/credentials', (req, res) => {
    res.json({
        facebook: {
            configured: validateCredentials('facebook'),
            fields: ['FB_EMAIL', 'FB_PASSWORD']
        },
        instagram: {
            configured: validateCredentials('instagram'),
            fields: ['IG_USERNAME', 'IG_PASSWORD']
        },
        twitter: {
            configured: validateCredentials('twitter'),
            fields: ['TWITTER_EMAIL', 'TWITTER_PASSWORD']
        }
    });
});

// Error handling middleware
app.use((err, req, res, next) => {
    console.error('Server error:', err);
    res.status(500).json({
        success: false,
        error: err.message || 'Internal server error'
    });
});

// Start server
app.listen(PORT, () => {
    console.log('='.repeat(60));
    console.log('🚀 Social Media MCP Server (Gold Tier)');
    console.log('='.repeat(60));
    console.log(`📡 Server running on port ${PORT}`);
    console.log('');
    console.log('Endpoints:');
    console.log('  POST /post-fb  - Post to Facebook');
    console.log('  POST /post-ig  - Post to Instagram');
    console.log('  POST /post-x   - Post to Twitter/X');
    console.log('  POST /post-all - Post to all platforms');
    console.log('  GET  /health   - Health check');
    console.log('  GET  /credentials - Check configured credentials');
    console.log('');
    console.log('Environment:');
    console.log(`  FB_EMAIL: ${CREDENTIALS.facebook.email ? '***' : 'not set'}`);
    console.log(`  IG_USERNAME: ${CREDENTIALS.instagram.username ? '***' : 'not set'}`);
    console.log(`  TWITTER_EMAIL: ${CREDENTIALS.twitter.email ? '***' : 'not set'}`);
    console.log('='.repeat(60));
});

module.exports = app;
