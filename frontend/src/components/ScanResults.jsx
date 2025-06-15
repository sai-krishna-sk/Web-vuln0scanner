// src/components/ScanResults.jsx
import React, { useEffect, useState } from "react";
import { 
  Shield, 
  Download, 
  FileText, 
  AlertTriangle, 
  CheckCircle, 
  XCircle, 
  Clock, 
  Globe, 
  Target,
  Filter,
  Zap,
  Bug,
  Eye
} from "lucide-react";

export default function ScanResults({ darkMode }) {
  const [scanData, setScanData] = useState(null);
  const [error, setError] = useState(null);
  const [downloadingHtml, setDownloadingHtml] = useState(false);
  const [selectedSeverity, setSelectedSeverity] = useState('all');

  // Whenever a new scan is fired by ScanForm:
  useEffect(() => {
    const handleNewScan = (e) => {
      setScanData(e.detail);
      setError(null);
    };
    window.addEventListener("new-scan", handleNewScan);
    return () => window.removeEventListener("new-scan", handleNewScan);
  }, []);

  if (!scanData) {
    return (
      <div className={`relative overflow-hidden rounded-2xl shadow-xl border transition-all duration-300 ${
        darkMode
          ? 'bg-gradient-to-br from-slate-800/90 to-gray-800/90 border-slate-700/60'
          : 'bg-gradient-to-br from-slate-50 to-slate-100 border-slate-200/60'
      }`}>
        <div className={`absolute inset-0 ${
          darkMode
            ? 'bg-gradient-to-r from-slate-500/5 to-slate-600/5'
            : 'bg-gradient-to-r from-slate-500/5 to-slate-600/5'
        }`}></div>
        <div className="relative p-12 text-center">
          <div className={`w-20 h-20 mx-auto mb-6 rounded-full flex items-center justify-center ${
            darkMode
              ? 'bg-gradient-to-r from-slate-700 to-slate-600'
              : 'bg-gradient-to-r from-slate-200 to-slate-300'
          }`}>
            <Shield className={`w-10 h-10 ${
              darkMode ? 'text-slate-400' : 'text-slate-500'
            }`} />
          </div>
          <h3 className={`text-xl font-semibold mb-2 ${
            darkMode ? 'text-slate-200' : 'text-slate-700'
          }`}>
            No Scans Yet
          </h3>
          <p className={`${
            darkMode ? 'text-slate-400' : 'text-slate-500'
          }`}>
            Start your first security scan to see results here
          </p>
        </div>
      </div>
    );
  }

  // Destructure for convenience
  const {
    target,
    total_vulnerabilities,
    unique_vulnerabilities,
    vulnerability_analysis: {
      total_severity_counts,
      unique_severity_counts,
      unique_results,
    },
  } = scanData;

  const getSeverityColor = (severity) => {
    if (darkMode) {
      const colors = {
        critical: 'from-red-600 to-red-700 text-white shadow-red-500/25',
        high: 'from-orange-600 to-red-600 text-white shadow-orange-500/25',
        medium: 'from-yellow-600 to-orange-600 text-white shadow-yellow-500/25',
        low: 'from-emerald-600 to-yellow-600 text-white shadow-emerald-500/25'
      };
      return colors[severity] || 'from-gray-600 to-gray-700 text-white shadow-gray-500/25';
    } else {
      const colors = {
        critical: 'from-red-500 to-red-600 text-white shadow-red-500/25',
        high: 'from-orange-500 to-red-500 text-white shadow-orange-500/25',
        medium: 'from-yellow-500 to-orange-500 text-white shadow-yellow-500/25',
        low: 'from-green-500 to-yellow-500 text-white shadow-green-500/25'
      };
      return colors[severity] || 'from-gray-500 to-gray-600 text-white shadow-gray-500/25';
    }
  };

  const getSeverityIcon = (severity) => {
    switch(severity) {
      case 'critical': return <Zap className="w-4 h-4" />;
      case 'high': return <AlertTriangle className="w-4 h-4" />;
      case 'medium': return <Clock className="w-4 h-4" />;
      case 'low': return <CheckCircle className="w-4 h-4" />;
      default: return <Shield className="w-4 h-4" />;
    }
  };

  const filteredResults = selectedSeverity === 'all' 
    ? unique_results 
    : unique_results.filter(vuln => vuln.severity === selectedSeverity);

  // Download JSON client-side
  const downloadJSON = () => {
    try {
      const filename = `scan_report_${Date.now()}.json`;
      const blob = new Blob(
        [JSON.stringify(scanData, null, 2)],
        { type: "application/json" }
      );
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
    } catch (err) {
      console.error(err);
      setError("Failed to generate JSON download.");
    }
  };

  // Download HTML via backend
  const downloadHTML = async () => {
    setError(null);
    setDownloadingHtml(true);
    try {
      const response = await fetch(
        `${process.env.REACT_APP_API_BASE_URL}/download/html`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ scan_data: scanData }),
        }
      );
      if (!response.ok) {
        const errJson = await response.json();
        throw new Error(errJson.error || "Failed to generate HTML report");
      }
      const blob = await response.blob();
      const filename = `scan_report_${Date.now()}.html`;
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
    } catch (err) {
      console.error(err);
      setError(err.message || "Unknown error downloading HTML.");
    } finally {
      setDownloadingHtml(false);
    }
  };

  return (
    <div className="space-y-8">
      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className={`relative overflow-hidden rounded-2xl shadow-lg border transition-all duration-300 hover:shadow-xl ${
          darkMode
            ? 'bg-gradient-to-br from-cyan-900/50 to-cyan-800/50 border-cyan-700/60'
            : 'bg-gradient-to-br from-blue-50 to-blue-100 border-blue-200/60'
        }`}>
          <div className={`absolute top-0 right-0 w-20 h-20 rounded-full -mr-10 -mt-10 ${
            darkMode
              ? 'bg-gradient-to-br from-cyan-400/20 to-cyan-500/20'
              : 'bg-gradient-to-br from-blue-400/20 to-blue-500/20'
          }`}></div>
          <div className="relative p-6">
            <div className="flex items-center gap-4">
              <div className={`p-3 rounded-xl shadow-lg ${
                darkMode
                  ? 'bg-gradient-to-r from-cyan-500 to-cyan-600'
                  : 'bg-gradient-to-r from-blue-500 to-blue-600'
              }`}>
                <Globe className="w-6 h-6 text-white" />
              </div>
              <div>
                <p className={`text-sm font-medium ${
                  darkMode ? 'text-cyan-300' : 'text-blue-600'
                }`}>
                  Target
                </p>
                <p className={`text-lg font-bold truncate ${
                  darkMode ? 'text-white' : 'text-slate-800'
                }`}>
                  {target}
                </p>
              </div>
            </div>
          </div>
        </div>

        <div className={`relative overflow-hidden rounded-2xl shadow-lg border transition-all duration-300 hover:shadow-xl ${
          darkMode
            ? 'bg-gradient-to-br from-red-900/50 to-red-800/50 border-red-700/60'
            : 'bg-gradient-to-br from-red-50 to-red-100 border-red-200/60'
        }`}>
          <div className={`absolute top-0 right-0 w-20 h-20 rounded-full -mr-10 -mt-10 ${
            darkMode
              ? 'bg-gradient-to-br from-red-400/20 to-red-500/20'
              : 'bg-gradient-to-br from-red-400/20 to-red-500/20'
          }`}></div>
          <div className="relative p-6">
            <div className="flex items-center gap-4">
              <div className={`p-3 rounded-xl shadow-lg ${
                darkMode
                  ? 'bg-gradient-to-r from-red-500 to-red-600'
                  : 'bg-gradient-to-r from-red-500 to-red-600'
              }`}>
                <Bug className="w-6 h-6 text-white" />
              </div>
              <div>
                <p className={`text-sm font-medium ${
                  darkMode ? 'text-red-300' : 'text-red-600'
                }`}>
                  Total Issues
                </p>
                <p className={`text-2xl font-bold ${
                  darkMode ? 'text-white' : 'text-slate-800'
                }`}>
                  {total_vulnerabilities}
                </p>
              </div>
            </div>
          </div>
        </div>

        <div className={`relative overflow-hidden rounded-2xl shadow-lg border transition-all duration-300 hover:shadow-xl ${
          darkMode
            ? 'bg-gradient-to-br from-emerald-900/50 to-emerald-800/50 border-emerald-700/60'
            : 'bg-gradient-to-br from-purple-50 to-purple-100 border-purple-200/60'
        }`}>
          <div className={`absolute top-0 right-0 w-20 h-20 rounded-full -mr-10 -mt-10 ${
            darkMode
              ? 'bg-gradient-to-br from-emerald-400/20 to-emerald-500/20'
              : 'bg-gradient-to-br from-purple-400/20 to-purple-500/20'
          }`}></div>
          <div className="relative p-6">
            <div className="flex items-center gap-4">
              <div className={`p-3 rounded-xl shadow-lg ${
                darkMode
                  ? 'bg-gradient-to-r from-emerald-500 to-emerald-600'
                  : 'bg-gradient-to-r from-purple-500 to-purple-600'
              }`}>
                <Eye className="w-6 h-6 text-white" />
              </div>
              <div>
                <p className={`text-sm font-medium ${
                  darkMode ? 'text-emerald-300' : 'text-purple-600'
                }`}>
                  Unique Issues
                </p>
                <p className={`text-2xl font-bold ${
                  darkMode ? 'text-white' : 'text-slate-800'
                }`}>
                  {unique_vulnerabilities}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Severity Breakdown */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className={`rounded-2xl shadow-xl p-8 border transition-all duration-300 ${
          darkMode
            ? 'bg-gradient-to-br from-slate-800/90 to-gray-800/90 border-slate-700/60'
            : 'bg-gradient-to-br from-white to-slate-50 border-slate-200/60'
        }`}>
          <h3 className={`text-xl font-bold mb-6 flex items-center gap-2 ${
            darkMode ? 'text-white' : 'text-slate-800'
          }`}>
            <div className={`p-2 rounded-lg ${
              darkMode
                ? 'bg-gradient-to-r from-cyan-500 to-emerald-600'
                : 'bg-gradient-to-r from-blue-500 to-purple-600'
            }`}>
              <Shield className="w-5 h-5 text-white" />
            </div>
            Total by Severity
          </h3>
          <div className="space-y-4">
            {Object.entries(total_severity_counts).map(([severity, count]) => (
              <div key={severity} className={`flex items-center justify-between p-4 rounded-xl shadow-sm border transition-all duration-200 hover:shadow-md ${
                darkMode
                  ? 'bg-slate-700/50 border-slate-600/50'
                  : 'bg-white border-slate-100'
              }`}>
                <div className="flex items-center gap-3">
                  <div className={`p-2 rounded-lg bg-gradient-to-r shadow-lg ${getSeverityColor(severity)}`}>
                    {getSeverityIcon(severity)}
                  </div>
                  <span className={`font-semibold capitalize ${
                    darkMode ? 'text-slate-200' : 'text-slate-700'
                  }`}>
                    {severity}
                  </span>
                </div>
                <span className={`text-xl font-bold ${
                  darkMode ? 'text-white' : 'text-slate-800'
                }`}>
                  {count}
                </span>
              </div>
            ))}
          </div>
        </div>

        <div className={`rounded-2xl shadow-xl p-8 border transition-all duration-300 ${
          darkMode
            ? 'bg-gradient-to-br from-slate-800/90 to-gray-800/90 border-slate-700/60'
            : 'bg-gradient-to-br from-white to-slate-50 border-slate-200/60'
        }`}>
          <h3 className={`text-xl font-bold mb-6 flex items-center gap-2 ${
            darkMode ? 'text-white' : 'text-slate-800'
          }`}>
            <div className={`p-2 rounded-lg ${
              darkMode
                ? 'bg-gradient-to-r from-emerald-500 to-cyan-600'
                : 'bg-gradient-to-r from-green-500 to-blue-600'
            }`}>
              <Target className="w-5 h-5 text-white" />
            </div>
            Unique by Severity
          </h3>
          <div className="space-y-4">
            {Object.entries(unique_severity_counts).map(([severity, count]) => (
              <div key={severity} className={`flex items-center justify-between p-4 rounded-xl shadow-sm border transition-all duration-200 hover:shadow-md ${
                darkMode
                  ? 'bg-slate-700/50 border-slate-600/50'
                  : 'bg-white border-slate-100'
              }`}>
                <div className="flex items-center gap-3">
                  <div className={`p-2 rounded-lg bg-gradient-to-r shadow-lg ${getSeverityColor(severity)}`}>
                    {getSeverityIcon(severity)}
                  </div>
                  <span className={`font-semibold capitalize ${
                    darkMode ? 'text-slate-200' : 'text-slate-700'
                  }`}>
                    {severity}
                  </span>
                </div>
                <span className={`text-xl font-bold ${
                  darkMode ? 'text-white' : 'text-slate-800'
                }`}>
                  {count}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Vulnerability Table */}
      <div className={`rounded-2xl shadow-xl border transition-all duration-300 ${
        darkMode
          ? 'bg-gradient-to-br from-slate-800/90 to-gray-800/90 border-slate-700/60'
          : 'bg-gradient-to-br from-white to-slate-50 border-slate-200/60'
      }`}>
        <div className={`p-8 border-b ${
          darkMode ? 'border-slate-700' : 'border-slate-200'
        }`}>
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <h3 className={`text-xl font-bold flex items-center gap-2 ${
              darkMode ? 'text-white' : 'text-slate-800'
            }`}>
              <div className={`p-2 rounded-lg ${
                darkMode
                  ? 'bg-gradient-to-r from-red-500 to-orange-600'
                  : 'bg-gradient-to-r from-red-500 to-orange-600'
              }`}>
                <AlertTriangle className="w-5 h-5 text-white" />
              </div>
              Vulnerability Details
            </h3>
            <div className="flex items-center gap-2">
              <Filter className={`w-4 h-4 ${
                darkMode ? 'text-slate-400' : 'text-slate-500'
              }`} />
              <div className="flex gap-2 flex-wrap">
                <button
                  onClick={() => setSelectedSeverity('all')}
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                    selectedSeverity === 'all'
                      ? darkMode
                        ? 'bg-gradient-to-r from-cyan-500 to-emerald-600 text-white shadow-lg shadow-cyan-500/25'
                        : 'bg-gradient-to-r from-blue-500 to-purple-600 text-white shadow-lg'
                      : darkMode
                        ? 'bg-slate-700 text-slate-300 hover:bg-slate-600'
                        : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                  }`}
                >
                  All
                </button>
                {Object.keys(unique_severity_counts).map(severity => (
                  <button
                    key={severity}
                    onClick={() => setSelectedSeverity(severity)}
                    className={`px-4 py-2 rounded-lg text-sm font-medium capitalize transition-all duration-200 ${
                      selectedSeverity === severity
                        ? `bg-gradient-to-r ${getSeverityColor(severity)} shadow-lg`
                        : darkMode
                          ? 'bg-slate-700 text-slate-300 hover:bg-slate-600'
                          : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                    }`}
                  >
                    {severity}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>

        <div className="p-8">
          <div className="space-y-4">
            {filteredResults.map((vuln, idx) => (
              <div key={idx} className={`p-6 rounded-xl shadow-sm border transition-all duration-200 hover:shadow-md ${
                darkMode
                  ? 'bg-slate-700/50 border-slate-600/50 hover:bg-slate-700/70'
                  : 'bg-white border-slate-100 hover:shadow-md'
              }`}>
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <div className={`p-2 rounded-lg bg-gradient-to-r shadow-lg ${getSeverityColor(vuln.severity)}`}>
                        {getSeverityIcon(vuln.severity)}
                      </div>
                      <div>
                        <h4 className={`font-bold ${
                          darkMode ? 'text-white' : 'text-slate-800'
                        }`}>
                          {vuln.type}
                        </h4>
                        <p className={`text-sm ${
                          darkMode ? 'text-slate-300' : 'text-slate-600'
                        }`}>
                          {vuln.description}
                        </p>
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-4">
                    <div className="text-center">
                      <p className={`text-2xl font-bold ${
                        darkMode ? 'text-white' : 'text-slate-800'
                      }`}>
                        {vuln.affected_urls_count}
                      </p>
                      <p className={`text-xs ${
                        darkMode ? 'text-slate-400' : 'text-slate-500'
                      }`}>
                        Affected URLs
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Error Message, if any */}
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

      {/* Download Buttons */}
      <div className={`rounded-2xl shadow-xl p-8 border transition-all duration-300 ${
        darkMode
          ? 'bg-gradient-to-br from-slate-800/90 to-emerald-900/20 border-emerald-700/30'
          : 'bg-gradient-to-br from-slate-50 to-blue-50 border-slate-200/60'
      }`}>
        <h3 className={`text-xl font-bold mb-6 flex items-center gap-2 ${
          darkMode ? 'text-white' : 'text-slate-800'
        }`}>
          <div className={`p-2 rounded-lg ${
            darkMode
              ? 'bg-gradient-to-r from-emerald-500 to-cyan-600'
              : 'bg-gradient-to-r from-green-500 to-blue-600'
          }`}>
            <Download className="w-5 h-5 text-white" />
          </div>
          Export Report
        </h3>
        <div className="flex flex-col sm:flex-row gap-4">
          <button
            onClick={downloadJSON}
            className={`flex-1 flex items-center justify-center gap-3 px-6 py-4 font-semibold rounded-xl shadow-lg transition-all duration-300 hover:scale-[1.02] active:scale-[0.98] ${
              darkMode
                ? 'bg-gradient-to-r from-emerald-500 to-emerald-600 text-white hover:from-emerald-600 hover:to-emerald-700 hover:shadow-xl hover:shadow-emerald-500/25'
                : 'bg-gradient-to-r from-green-500 to-green-600 text-white hover:from-green-600 hover:to-green-700 hover:shadow-xl'
            }`}
          >
            <FileText className="w-5 h-5" />
            Download JSON
          </button>

          <button
            onClick={downloadHTML}
            disabled={downloadingHtml}
            className={`flex-1 flex items-center justify-center gap-3 px-6 py-4 font-semibold rounded-xl shadow-lg transition-all duration-300 ${
              downloadingHtml
                ? 'bg-slate-400 text-white cursor-not-allowed'
                : darkMode
                  ? 'bg-gradient-to-r from-cyan-500 to-cyan-600 text-white hover:from-cyan-600 hover:to-cyan-700 hover:shadow-xl hover:shadow-cyan-500/25 hover:scale-[1.02] active:scale-[0.98]'
                  : 'bg-gradient-to-r from-blue-500 to-blue-600 text-white hover:from-blue-600 hover:to-blue-700 hover:shadow-xl hover:scale-[1.02] active:scale-[0.98]'
            }`}
          >
            {downloadingHtml ? (
              <>
                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                Generating HTML...
              </>
            ) : (
              <>
                <FileText className="w-5 h-5" />
                Download HTML
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}