// src/App.js
import React, { useState, useEffect } from "react";
import { Shield, Moon, Sun } from "lucide-react";
import ScanForm from "./components/ScanForm";
import ScanResults from "./components/ScanResults";

function App() {
  const [darkMode, setDarkMode] = useState(false);

  // Load dark mode preference from localStorage
  useEffect(() => {
    const savedTheme = localStorage.getItem('darkMode');
    if (savedTheme) {
      setDarkMode(JSON.parse(savedTheme));
    } else {
      // Default to system preference
      setDarkMode(window.matchMedia('(prefers-color-scheme: dark)').matches);
    }
  }, []);

  // Save dark mode preference and apply to document
  useEffect(() => {
    localStorage.setItem('darkMode', JSON.stringify(darkMode));
    if (darkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [darkMode]);

  const toggleDarkMode = () => {
    setDarkMode(!darkMode);
  };

  return (
    <div className={`min-h-screen transition-colors duration-300 ${
      darkMode 
        ? 'bg-gradient-to-br from-slate-900 via-gray-900 to-black' 
        : 'bg-gradient-to-br from-slate-100 via-blue-50 to-purple-50'
    }`}>
      {/* Header */}
      <header className={`relative overflow-hidden shadow-2xl transition-colors duration-300 ${
        darkMode
          ? 'bg-gradient-to-r from-slate-900 via-cyan-900 to-emerald-900'
          : 'bg-gradient-to-r from-slate-900 via-blue-900 to-purple-900'
      }`}>
        <div className={`absolute inset-0 ${
          darkMode 
            ? 'bg-gradient-to-r from-cyan-600/20 to-emerald-600/20' 
            : 'bg-gradient-to-r from-blue-600/20 to-purple-600/20'
        }`}></div>
        <div className="absolute inset-0">
          <div className={`absolute top-0 left-1/4 w-72 h-72 rounded-full blur-3xl ${
            darkMode ? 'bg-cyan-500/10' : 'bg-blue-500/10'
          }`}></div>
          <div className={`absolute bottom-0 right-1/4 w-96 h-96 rounded-full blur-3xl ${
            darkMode ? 'bg-emerald-500/10' : 'bg-purple-500/10'
          }`}></div>
        </div>
        
        {/* Dark Mode Toggle */}
        <div className="absolute top-6 right-6 z-10">
          <button
            onClick={toggleDarkMode}
            className={`p-3 rounded-full shadow-lg backdrop-blur-sm border transition-all duration-300 hover:scale-110 ${
              darkMode
                ? 'bg-slate-800/80 border-cyan-500/30 text-cyan-400 hover:bg-slate-700/80'
                : 'bg-white/20 border-white/30 text-white hover:bg-white/30'
            }`}
            aria-label="Toggle dark mode"
          >
            {darkMode ? (
              <Sun className="w-5 h-5" />
            ) : (
              <Moon className="w-5 h-5" />
            )}
          </button>
        </div>

        <div className="relative max-w-7xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <div className="inline-flex items-center gap-4 mb-6">
              <div className={`p-4 rounded-2xl shadow-2xl ${
                darkMode
                  ? 'bg-gradient-to-r from-cyan-500 to-emerald-600'
                  : 'bg-gradient-to-r from-blue-500 to-purple-600'
              }`}>
                <Shield className="w-12 h-12 text-white" />
              </div>
              <div className="text-left">
                <h1 className="text-4xl md:text-5xl font-bold text-white mb-2">
                  Security Scanner
                </h1>
                <p className={`text-lg ${
                  darkMode ? 'text-cyan-200' : 'text-blue-200'
                }`}>
                  Advanced Web Vulnerability Analysis
                </p>
              </div>
            </div>
            <p className={`text-lg max-w-2xl mx-auto ${
              darkMode ? 'text-slate-400' : 'text-slate-300'
            }`}>
              Identify security vulnerabilities and protect your web applications with comprehensive automated scanning
            </p>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="max-w-7xl mx-auto py-12 px-4 sm:px-6 lg:px-8 space-y-12">
        {/* 1) Form to trigger a new scan */}
        <div>
          <ScanForm darkMode={darkMode} />
        </div>

        {/* 2) Display results of the most recent scan */}
        <div>
          <ScanResults darkMode={darkMode} />
        </div>
      </main>
    </div>
  );
}

export default App;