// src/components/ScanForm.jsx
import React, { useState } from "react";
import { Target, Globe, Search, XCircle, Activity } from "lucide-react";

export default function ScanForm({ darkMode }) {
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [lastScanData, setLastScanData] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);

    if (!url.trim()) {
      setError("Please enter a valid URL.");
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(
        `${process.env.REACT_APP_API_BASE_URL}/scan`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ url: url.trim() }),
        }
      );

      if (!response.ok) {
        const errJson = await response.json();
        throw new Error(errJson.error || "Scan request failed");
      }

      const data = await response.json();
      setLastScanData(data);

      // Fire a global event so ScanResults can update
      window.dispatchEvent(new CustomEvent("new-scan", { detail: data }));
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={`relative overflow-hidden rounded-2xl shadow-xl backdrop-blur-sm border transition-all duration-300 ${
      darkMode
        ? 'bg-gradient-to-br from-slate-800/90 to-gray-800/90 border-cyan-500/20'
        : 'bg-gradient-to-br from-slate-50 to-blue-50 border-slate-200/60'
    }`}>
      <div className={`absolute inset-0 ${
        darkMode
          ? 'bg-gradient-to-r from-cyan-500/5 to-emerald-500/5'
          : 'bg-gradient-to-r from-blue-500/5 to-purple-500/5'
      }`}></div>
      
      {/* Animated background elements */}
      <div className="absolute inset-0 overflow-hidden">
        <div className={`absolute -top-4 -right-4 w-24 h-24 rounded-full blur-xl opacity-20 ${
          darkMode ? 'bg-cyan-500' : 'bg-blue-500'
        }`}></div>
        <div className={`absolute -bottom-4 -left-4 w-32 h-32 rounded-full blur-xl opacity-20 ${
          darkMode ? 'bg-emerald-500' : 'bg-purple-500'
        }`}></div>
      </div>

      <div className="relative p-8">
        <div className="flex items-center gap-3 mb-6">
          <div className={`p-3 rounded-xl shadow-lg ${
            darkMode
              ? 'bg-gradient-to-r from-cyan-500 to-emerald-600'
              : 'bg-gradient-to-r from-blue-500 to-purple-600'
          }`}>
            <Target className="w-6 h-6 text-white" />
          </div>
          <div>
            <h3 className={`text-xl font-bold ${
              darkMode ? 'text-white' : 'text-slate-800'
            }`}>
              Start Security Scan
            </h3>
            <p className={`${
              darkMode ? 'text-slate-300' : 'text-slate-600'
            }`}>
              Enter a URL to analyze for vulnerabilities
            </p>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="relative">
            <label
              htmlFor="target-url"
              className={`block text-sm font-semibold mb-2 ${
                darkMode ? 'text-slate-200' : 'text-slate-700'
              }`}
            >
              Target URL
            </label>
            <div className="relative">
              <Globe className={`absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 ${
                darkMode ? 'text-slate-400' : 'text-slate-400'
              }`} />
              <input
                id="target-url"
                type="text"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder="https://example.com"
                className={`w-full pl-12 pr-4 py-4 backdrop-blur-sm border rounded-xl shadow-sm transition-all duration-200 ${
                  darkMode
                    ? 'bg-slate-700/80 border-slate-600 text-white placeholder-slate-400 focus:ring-4 focus:ring-cyan-500/20 focus:border-cyan-500'
                    : 'bg-white/80 border-slate-200 text-slate-800 placeholder-slate-400 focus:ring-4 focus:ring-blue-500/20 focus:border-blue-500'
                }`}
              />
            </div>
          </div>

          {error && (
            <div className={`flex items-center gap-2 p-4 rounded-xl border ${
              darkMode
                ? 'bg-red-900/50 border-red-700/50 backdrop-blur-sm'
                : 'bg-red-50 border-red-200'
            }`}>
              <XCircle className="w-5 h-5 text-red-500 flex-shrink-0" />
              <p className={`text-sm ${
                darkMode ? 'text-red-300' : 'text-red-700'
              }`}>
                {error}
              </p>
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className={`w-full relative overflow-hidden px-6 py-4 rounded-xl font-semibold text-white shadow-lg transition-all duration-300 ${
              loading
                ? 'bg-slate-400 cursor-not-allowed'
                : darkMode
                  ? 'bg-gradient-to-r from-cyan-600 to-emerald-600 hover:from-cyan-700 hover:to-emerald-700 hover:shadow-xl hover:shadow-cyan-500/25 hover:scale-[1.02] active:scale-[0.98]'
                  : 'bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 hover:shadow-xl hover:scale-[1.02] active:scale-[0.98]'
            }`}
          >
            <div className="flex items-center justify-center gap-3">
              {loading ? (
                <>
                  <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  <span>Scanning...</span>
                </>
              ) : (
                <>
                  <Search className="w-5 h-5" />
                  <span>Start Security Scan</span>
                </>
              )}
            </div>
            {!loading && (
              <div className="absolute inset-0 bg-gradient-to-r from-white/20 to-transparent opacity-0 hover:opacity-100 transition-opacity duration-300" />
            )}
          </button>
        </form>

        {/* Optionally show a mini-timestamp of last scan */}
        {lastScanData && (
          <div className={`mt-8 p-4 backdrop-blur-sm rounded-xl border transition-all duration-300 ${
            darkMode
              ? 'bg-slate-700/60 border-slate-600/60'
              : 'bg-white/60 border-slate-200/60'
          }`}>
            <div className="flex items-center gap-2 mb-2">
              <div className={`w-2 h-2 rounded-full animate-pulse ${
                darkMode ? 'bg-emerald-400' : 'bg-green-500'
              }`}></div>
              <p className={`text-sm font-medium ${
                darkMode ? 'text-slate-200' : 'text-slate-700'
              }`}>
                Last scan completed
              </p>
            </div>
            <div className="flex items-center gap-2">
              <Activity className={`w-4 h-4 ${
                darkMode ? 'text-cyan-400' : 'text-blue-600'
              }`} />
              <p className={`text-sm ${
                darkMode ? 'text-slate-300' : 'text-slate-600'
              }`}>
                {new Date().toLocaleString()}
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}