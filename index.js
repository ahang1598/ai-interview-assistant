/**
 * AI Interview Assistant - Frontend Server
 * 
 * A tool to serve the frontend files for AI interview preparation
 */

const express = require('express');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000;

// 获取正确的根目录路径
const rootPath = process.env.NODE_PATH || path.resolve(__dirname);

// Serve static files from the 'src' directory
app.use(express.static(path.join(rootPath, 'src')));

// Serve index.html for the root route
app.get('/', (req, res) => {
  res.sendFile(path.join(rootPath, 'src', 'index.html'));
});

// Start the server
app.listen(PORT, () => {
  console.log(`AI Interview Assistant frontend server listening at http://localhost:${PORT}`);
});