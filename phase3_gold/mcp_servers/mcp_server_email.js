#!/usr/bin/env node
/**
 * Email MCP Server - Gold Tier
 * ============================
 * Send emails with attachments via Gmail
 * 
 * Port: 3003
 * Endpoints:
 *   POST /send-email      - Send email
 *   POST /send-invoice    - Send invoice with attachment
 *   GET  /health          - Health check
 *   GET  /stats           - Server statistics
 */

import express from 'express';
import cors from 'cors';
import nodemailer from 'nodemailer';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const app = express();
const PORT = 3003;

// Middleware
app.use(cors());
app.use(express.json({ limit: '10mb' }));

// Load environment variables
import dotenv from 'dotenv';
dotenv.config({ path: path.join(__dirname, '..', '.env') });

// Gmail configuration
const GMAIL_EMAIL = process.env.GMAIL_EMAIL || '';
const GMAIL_PASSWORD = process.env.GMAIL_PASSWORD || '';

// Create transporter
const createTransporter = () => {
  return nodemailer.createTransport({
    service: 'gmail',
    auth: {
      user: GMAIL_EMAIL,
      pass: GMAIL_PASSWORD
    }
  });
};

// Store server stats
const stats = {
  requests: 0,
  emails_sent: 0,
  emails_failed: 0,
  invoices_sent: 0,
  startTime: new Date().toISOString()
};

// Logs directory
const LOGS_DIR = path.join(__dirname, '..', 'Logs');
if (!fs.existsSync(LOGS_DIR)) {
  fs.mkdirSync(LOGS_DIR, { recursive: true });
}

// Health check endpoint
app.get('/health', (req, res) => {
  stats.requests++;
  res.json({
    status: 'healthy',
    service: 'email-mcp-server',
    port: PORT,
    credentials_set: !!(GMAIL_EMAIL && GMAIL_PASSWORD),
    uptime: Date.now() - new Date(stats.startTime).getTime(),
    stats: stats
  });
});

// Get stats endpoint
app.get('/stats', (req, res) => {
  stats.requests++;
  res.json({
    service: 'email-mcp-server',
    stats: stats
  });
});

// Send email endpoint
app.post('/send-email', async (req, res) => {
  stats.requests++;
  
  const { to, subject, body, html = false, attachment } = req.body;
  
  // Validation
  if (!to || !subject || !body) {
    return res.status(400).json({ 
      success: false, 
      error: 'Missing required fields: to, subject, body' 
    });
  }
  
  if (!GMAIL_EMAIL || !GMAIL_PASSWORD) {
    return res.status(500).json({ 
      success: false, 
      error: 'Gmail credentials not configured. Set GMAIL_EMAIL and GMAIL_PASSWORD in .env' 
    });
  }
  
  try {
    const transporter = createTransporter();
    
    // Prepare email options
    const mailOptions = {
      from: GMAIL_EMAIL,
      to: to,
      subject: subject,
      text: html ? undefined : body,
      html: html ? body : undefined
    };
    
    // Add attachment if provided
    if (attachment) {
      if (fs.existsSync(attachment)) {
        mailOptions.attachments = [
          {
            filename: path.basename(attachment),
            path: attachment
          }
        ];
        console.log(`Attachment added: ${attachment}`);
      } else {
        console.warn(`Attachment not found: ${attachment}`);
      }
    }
    
    // Send email
    const info = await transporter.sendMail(mailOptions);
    
    stats.emails_sent++;
    
    // Log transaction
    logTransaction('email', { to, subject, attachment, messageId: info.messageId });
    
    res.json({
      success: true,
      message: 'Email sent successfully',
      messageId: info.messageId,
      timestamp: new Date().toISOString()
    });
    
  } catch (error) {
    stats.emails_failed++;
    console.error('Send email error:', error);
    
    res.status(500).json({
      success: false,
      error: error.message || 'Failed to send email'
    });
  }
});

// Send invoice endpoint (specialized for invoices)
app.post('/send-invoice', async (req, res) => {
  stats.requests++;
  
  const { 
    to, 
    invoice_number, 
    invoice_path, 
    amount,
    client_name 
  } = req.body;
  
  // Validation
  if (!to || !invoice_number || !invoice_path) {
    return res.status(400).json({ 
      success: false, 
      error: 'Missing required fields: to, invoice_number, invoice_path' 
    });
  }
  
  if (!GMAIL_EMAIL || !GMAIL_PASSWORD) {
    return res.status(500).json({ 
      success: false, 
      error: 'Gmail credentials not configured' 
    });
  }
  
  try {
    const transporter = createTransporter();
    
    // Create professional email body
    const emailBody = `
Dear ${client_name || 'Valued Client'},

Please find attached your invoice ${invoice_number} for the amount of $${amount}.

Payment is due within 30 days of receipt.

If you have any questions, please don't hesitate to contact us.

Thank you for your business!

Best regards,
AI Employee Services
${GMAIL_EMAIL}
    `.trim();
    
    // Prepare email options
    const mailOptions = {
      from: GMAIL_EMAIL,
      to: to,
      subject: `Invoice ${invoice_number} - $${amount}`,
      text: emailBody,
      attachments: []
    };
    
    // Add invoice attachment
    if (fs.existsSync(invoice_path)) {
      mailOptions.attachments.push({
        filename: path.basename(invoice_path),
        path: invoice_path
      });
    } else {
      console.warn(`Invoice file not found: ${invoice_path}`);
    }
    
    // Send email
    const info = await transporter.sendMail(mailOptions);
    
    stats.invoices_sent++;
    
    // Log transaction
    logTransaction('invoice', { 
      to, 
      invoice_number, 
      amount, 
      invoice_path,
      messageId: info.messageId 
    });
    
    res.json({
      success: true,
      message: 'Invoice sent successfully',
      messageId: info.messageId,
      timestamp: new Date().toISOString()
    });
    
  } catch (error) {
    stats.emails_failed++;
    console.error('Send invoice error:', error);
    
    res.status(500).json({
      success: false,
      error: error.message || 'Failed to send invoice'
    });
  }
});

// Helper function to log transactions
function logTransaction(type, data) {
  const timestamp = new Date().toISOString();
  const logEntry = {
    timestamp,
    type,
    ...data
  };
  
  const logFile = path.join(LOGS_DIR, 'email_mcp_transactions.jsonl');
  fs.appendFileSync(logFile, JSON.stringify(logEntry) + '\n');
  
  // Also log to daily file
  const dateStr = new Date().toISOString().split('T')[0];
  const dailyLogFile = path.join(LOGS_DIR, `${dateStr}.json`);
  
  let dailyLogs = [];
  if (fs.existsSync(dailyLogFile)) {
    try {
      dailyLogs = JSON.parse(fs.readFileSync(dailyLogFile, 'utf-8'));
    } catch (e) {
      dailyLogs = [];
    }
  }
  
  dailyLogs.push(logEntry);
  fs.writeFileSync(dailyLogFile, JSON.stringify(dailyLogs, null, 2));
  
  console.log(`Transaction logged: ${type} to ${data.to}`);
}

// Start server
app.listen(PORT, () => {
  console.log('📧 Email MCP Server running on port', PORT);
  console.log('   Endpoints:');
  console.log('   POST /send-email       - Send email');
  console.log('   POST /send-invoice     - Send invoice with attachment');
  console.log('   GET  /health           - Health check');
  console.log('   GET  /stats            - Server statistics');
  console.log('');
  console.log('   Gmail:', GMAIL_EMAIL || 'NOT CONFIGURED');
  console.log('   Started at:', stats.startTime);
  console.log('');
  console.log('Example usage:');
  console.log('   curl -X POST http://localhost:3003/send-email \\');
  console.log('     -H "Content-Type: application/json" \\');
  console.log('     -d \'{"to":"client@example.com","subject":"Test","body":"Hello"}\'');
});
