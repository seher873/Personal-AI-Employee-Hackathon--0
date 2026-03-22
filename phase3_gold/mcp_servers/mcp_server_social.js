#!/usr/bin/env node
/**
 * Social Media MCP Server
 * Gold Tier - Requirement #6
 * 
 * Port: 3000
 * Endpoints:
 *   POST /post-fb   - Post to Facebook
 *   POST /post-ig   - Post to Instagram
 *   POST /post-x    - Post to Twitter/X
 *   POST /post-all  - Broadcast to all platforms
 *   GET  /health    - Health check
 */

import express from 'express';
import cors from 'cors';
import { spawn } from 'child_process';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const app = express();
const PORT = 3000;

// Middleware
app.use(cors());
app.use(express.json());

// Store server stats
const stats = {
  requests: 0,
  posts: {
    facebook: 0,
    instagram: 0,
    twitter: 0,
    linkedin: 0
  },
  startTime: new Date().toISOString()
};

// Health check endpoint
app.get('/health', (req, res) => {
  stats.requests++;
  res.json({
    status: 'healthy',
    service: 'social-mcp-server',
    port: PORT,
    uptime: Date.now() - new Date(stats.startTime).getTime(),
    stats: stats
  });
});

// Post to Facebook
app.post('/post-fb', async (req, res) => {
  stats.requests++;
  const { text, image_path } = req.body;
  
  if (!text) {
    return res.status(400).json({ error: 'Text is required' });
  }
  
  try {
    const result = await runPythonSkill('skill_facebook.py', text, image_path);
    stats.posts.facebook++;
    res.json({
      success: true,
      platform: 'facebook',
      result: result
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Post to Instagram
app.post('/post-ig', async (req, res) => {
  stats.requests++;
  const { text, image_path } = req.body;
  
  if (!text) {
    return res.status(400).json({ error: 'Text is required' });
  }
  
  if (!image_path) {
    return res.status(400).json({ error: 'Image path is required for Instagram' });
  }
  
  try {
    const result = await runPythonSkill('skill_instagram.py', text, image_path);
    stats.posts.instagram++;
    res.json({
      success: true,
      platform: 'instagram',
      result: result
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Post to Twitter/X
app.post('/post-x', async (req, res) => {
  stats.requests++;
  const { text } = req.body;

  if (!text) {
    return res.status(400).json({ error: 'Text is required' });
  }

  if (text.length > 280) {
    return res.status(400).json({ error: 'Text must be 280 characters or less' });
  }

  try {
    const result = await runPythonSkill('skill_twitter.py', text, null);
    stats.posts.twitter++;
    res.json({
      success: true,
      platform: 'twitter',
      result: result
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Post to LinkedIn
app.post('/post-linkedin', async (req, res) => {
  stats.requests++;
  const { text, image_path, company } = req.body;

  if (!text) {
    return res.status(400).json({ error: 'Text is required' });
  }

  try {
    const result = await runPythonSkill('skill_linkedin_api.py', text, image_path || '', company || false);
    stats.posts.linkedin++;
    res.json({
      success: true,
      platform: 'linkedin',
      result: result
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Post to all platforms
app.post('/post-all', async (req, res) => {
  stats.requests++;
  const { text, image_path } = req.body;

  if (!text) {
    return res.status(400).json({ error: 'Text is required' });
  }

  try {
    const results = await Promise.all([
      runPythonSkill('skill_facebook.py', text, image_path).catch(e => ({ error: e.message })),
      runPythonSkill('skill_instagram.py', text, image_path || 'post_image.png').catch(e => ({ error: e.message })),
      runPythonSkill('skill_twitter.py', text, null).catch(e => ({ error: e.message })),
      runPythonSkill('skill_linkedin_api.py', text, image_path || '', false).catch(e => ({ error: e.message }))
    ]);

    stats.posts.facebook++;
    stats.posts.instagram++;
    stats.posts.twitter++;
    stats.posts.linkedin++;

    res.json({
      success: true,
      platforms: {
        facebook: results[0],
        instagram: results[1],
        twitter: results[2],
        linkedin: results[3]
      }
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Get stats
app.get('/stats', (req, res) => {
  stats.requests++;
  res.json({
    service: 'social-mcp-server',
    stats: stats
  });
});

// Helper function to run Python skills
function runPythonSkill(skillFile, text, imagePath) {
  return new Promise((resolve, reject) => {
    // Skills are in Skills/ subdirectory
    const skillPath = path.join(__dirname, '..', 'Skills', skillFile);
    let output = '';
    let errorOutput = '';

    const args = [skillPath];

    const python = spawn('py', args, {
      cwd: path.join(__dirname, '..', 'Skills'),
      env: {
        ...process.env,
        PYTHONIOENCODING: 'utf-8'
      }
    });
    
    python.stdout.on('data', (data) => {
      output += data.toString();
    });
    
    python.stderr.on('data', (data) => {
      errorOutput += data.toString();
    });
    
    python.on('close', (code) => {
      if (code === 0) {
        resolve({ success: true, output: output.substring(0, 500) });
      } else {
        reject(new Error(errorOutput || `Exit code: ${code}`));
      }
    });
    
    python.on('error', (err) => {
      reject(err);
    });
  });
}

// Start server
app.listen(PORT, () => {
  console.log(`🚀 Social Media MCP Server running on port ${PORT}`);
  console.log(`   Endpoints:`);
  console.log(`   POST /post-fb   - Post to Facebook`);
  console.log(`   POST /post-ig   - Post to Instagram`);
  console.log(`   POST /post-x    - Post to Twitter/X`);
  console.log(`   POST /post-linkedin - Post to LinkedIn`);
  console.log(`   POST /post-all  - Post to all platforms`);
  console.log(`   GET  /health    - Health check`);
  console.log(`   GET  /stats     - Server statistics`);
  console.log(`\n   Started at: ${stats.startTime}`);
});
