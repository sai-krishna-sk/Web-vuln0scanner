import React from 'react';
import { createRoot } from 'react-dom/client';
import './index.css';
import App from './App';

// Find the root DOM node (as before)
const container = document.getElementById('root');

// Create a React 18 root
const root = createRoot(container);

// Render the <App/> inside that root
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
