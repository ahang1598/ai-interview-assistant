/**
 * AI Interview Assistant - Frontend Server
 * 
 * A tool to serve the frontend files for AI interview preparation
 */

const express = require('express');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000;

// Serve static files from the 'src' directory
app.use(express.static(path.join(__dirname)));

// Serve index.html for the root route
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'index.html'));
});

// Serve auth.html for the /auth route
app.get('/auth', (req, res) => {
  res.sendFile(path.join(__dirname, 'auth.html'));
});

// Start the server
app.listen(PORT, () => {
  console.log(`AI Interview Assistant frontend server listening at http://localhost:${PORT}`);
});