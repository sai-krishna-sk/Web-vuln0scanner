import html
import os
import json
from datetime import datetime
from urllib.parse import urlparse

def safe_html_escape(text):
    """Safely escape HTML content to prevent XSS in reports"""
    if text is None:
        return "N/A"
    return html.escape(str(text), quote=True)

def generate_html_report(scan_data, target_url):
    """Generate HTML report from scan data with page filtering functionality"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Safely escape the target URL
    safe_target_url = safe_html_escape(target_url)
    
    # Severity color mapping
    severity_colors = {
        "Critical": "#dc3545",
        "High": "#fd7e14", 
        "Medium": "#ffc107",
        "Low": "#28a745",
        "Info": "#17a2b8"
    }
    
    # Get vulnerability analysis
    vuln_analysis = scan_data.get('vulnerability_analysis', {})
    total_severity_counts = vuln_analysis.get('total_severity_counts', {})
    unique_severity_counts = vuln_analysis.get('unique_severity_counts', {})
    
    # Get unique URLs from results for filtering
    unique_urls = set()
    for result in scan_data.get('results', []):
        if result.get('url'):
            unique_urls.add(result['url'])
    
    # Sort URLs for consistent display
    sorted_urls = sorted(list(unique_urls))
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta http-equiv="Content-Security-Policy" content="default-src 'self'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; object-src 'none'; base-uri 'self'; form-action 'none';">
        <title>Security Scan Report - {safe_html_escape(target_url)}</title>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 20px;
                background-color: #f5f5f5;
                line-height: 1.6;
            }}
            .container {{
                max-width: 1200px;
                margin: 0 auto;
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            .header {{
                text-align: center;
                margin-bottom: 30px;
                padding-bottom: 20px;
                border-bottom: 2px solid #e9ecef;
            }}
            .header h1 {{
                color: #2c3e50;
                margin-bottom: 10px;
            }}
            .header .timestamp {{
                color: #6c757d;
                font-size: 14px;
            }}
            .filter-section {{
                background: #f8f9fa;
                padding: 20px;
                border-radius: 8px;
                margin-bottom: 30px;
                border-left: 4px solid #007bff;
            }}
            .filter-section h3 {{
                margin-top: 0;
                color: #495057;
            }}
            .filter-controls {{
                display: flex;
                gap: 15px;
                align-items: center;
                flex-wrap: wrap;
            }}
            .filter-select {{
                padding: 8px 12px;
                border: 2px solid #dee2e6;
                border-radius: 5px;
                background: white;
                color: #495057;
                font-size: 14px;
                min-width: 200px;
                max-width: 400px;
            }}
            .filter-select:focus {{
                outline: none;
                border-color: #007bff;
                box-shadow: 0 0 0 2px rgba(0,123,255,0.25);
            }}
            .filter-stats {{
                display: flex;
                gap: 20px;
                margin-top: 15px;
                flex-wrap: wrap;
            }}
            .filter-stat {{
                background: white;
                padding: 10px 15px;
                border-radius: 5px;
                border: 1px solid #dee2e6;
                font-size: 14px;
            }}
            .filter-stat strong {{
                color: #007bff;
            }}
            .summary {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }}
            .summary-card {{
                background: #f8f9fa;
                padding: 20px;
                border-radius: 8px;
                text-align: center;
                border-left: 4px solid #007bff;
            }}
            .summary-card h3 {{
                margin: 0 0 10px 0;
                color: #495057;
                font-size: 14px;
            }}
            .summary-card .value {{
                font-size: 24px;
                font-weight: bold;
                color: #007bff;
            }}
            .summary-card .subtitle {{
                font-size: 12px;
                color: #6c757d;
                margin-top: 5px;
            }}
            .severity-summary {{
                margin-bottom: 30px;
            }}
            .severity-tabs {{
                display: flex;
                margin-bottom: 20px;
                border-bottom: 2px solid #e9ecef;
            }}
            .severity-tab {{
                padding: 10px 20px;
                background: #f8f9fa;
                border: none;
                cursor: pointer;
                font-size: 14px;
                font-weight: bold;
                color: #495057;
                border-radius: 5px 5px 0 0;
                margin-right: 5px;
                transition: all 0.3s ease;
            }}
            .severity-tab.active {{
                background: #007bff;
                color: white;
            }}
            .severity-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                gap: 15px;
            }}
            .severity-card {{
                background: white;
                padding: 15px;
                border-radius: 8px;
                text-align: center;
                border: 2px solid #e9ecef;
            }}
            .results-section {{
                margin-top: 30px;
            }}
            .result-item {{
                background: white;
                margin-bottom: 15px;
                border-radius: 8px;
                border-left: 4px solid #6c757d;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                transition: opacity 0.3s ease;
            }}
            .result-item.hidden {{
                display: none;
            }}
            .result-header {{
                padding: 15px 20px;
                background: #f8f9fa;
                border-bottom: 1px solid #e9ecef;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }}
            .result-body {{
                padding: 20px;
            }}
            .severity-badge {{
                padding: 4px 12px;
                border-radius: 20px;
                color: white;
                font-size: 12px;
                font-weight: bold;
                text-transform: uppercase;
            }}
            .affected-urls {{
                background: #f8f9fa;
                padding: 15px;
                border-radius: 5px;
                margin: 15px 0;
            }}
            .affected-urls h4 {{
                margin-top: 0;
                color: #495057;
            }}
            .url-item {{
                padding: 5px 0;
                border-bottom: 1px solid #e9ecef;
                word-break: break-all;
                font-size: 14px;
            }}
            .url-item:last-child {{
                border-bottom: none;
            }}
            .url-count-badge {{
                background: #007bff;
                color: white;
                padding: 2px 8px;
                border-radius: 12px;
                font-size: 11px;
                font-weight: bold;
                margin-left: 10px;
            }}
            .no-results {{
                text-align: center;
                padding: 40px;
                color: #6c757d;
            }}
            .collapsible {{
                background-color: #f1f1f1;
                color: #333;
                cursor: pointer;
                padding: 15px;
                width: 100%;
                border: none;
                text-align: left;
                outline: none;
                font-size: 16px;
                border-radius: 5px;
                margin-bottom: 10px;
                transition: background-color 0.3s;
            }}
            .collapsible:hover {{
                background-color: #ddd;
            }}
            .collapsible.active {{
                background-color: #007bff;
                color: white;
            }}
            .collapsible-content {{
                max-height: 200px;
                overflow-y: auto;
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 0 0 5px 5px;
                margin-bottom: 20px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Security Scan Report</h1>
                <div class="timestamp">Generated on {timestamp}</div>
                <div style="margin-top: 10px; font-weight: bold; color: #007bff;">Target: {safe_target_url}</div>
            </div>
            
            <div class="filter-section">
                <h3>🔍 Filter Results by Page</h3>
                <div class="filter-controls">
                    <select id="pageFilter" class="filter-select" onchange="filterResults()">
                        <option value="all">All Pages (Show All Results)</option>"""
    
    # Add options for each unique URL
    for url in sorted_urls:
        safe_url = safe_html_escape(url)
        # Create a shorter display name for the option
        display_url = url
        if len(display_url) > 50:
            display_url = display_url[:47] + "..."
        safe_display_url = safe_html_escape(display_url)
        html_content += f'<option value="{safe_url}">{safe_display_url}</option>'
    
    html_content += f"""
                    </select>
                </div>
                <div class="filter-stats">
                    <div class="filter-stat">
                        <strong id="visibleResults">{len(scan_data.get('results', []))}</strong> results shown
                    </div>
                    <div class="filter-stat">
                        <strong id="totalResults">{len(scan_data.get('results', []))}</strong> total results
                    </div>
                </div>
            </div>
            
            <div class="summary">
                <div class="summary-card">
                    <h3>Total URLs Scanned</h3>
                    <div class="value">{len(scan_data.get('discovered_urls', []))}</div>
                </div>
                <div class="summary-card">
                    <h3>Total Issues Found</h3>
                    <div class="value">{scan_data.get('total_vulnerabilities', 0)}</div>
                    <div class="subtitle">All occurrences</div>
                </div>
                <div class="summary-card">
                    <h3>Unique Issues Found</h3>
                    <div class="value">{vuln_analysis.get('unique_count', 0)}</div>
                    <div class="subtitle">Distinct vulnerability types</div>
                </div>
                <div class="summary-card">
                    <h3>Pages with Issues</h3>
                    <div class="value">{len(sorted_urls)}</div>
                </div>
            </div>
    """
    
    # Add severity summary with tabs for total vs unique
    if total_severity_counts or unique_severity_counts:
        html_content += f"""
            <div class="severity-summary">
                <h2>Issues by Severity</h2>
                <div class="severity-tabs">
                    <button class="severity-tab active" onclick="showSeverityView('total')">Total Issues ({scan_data.get('total_vulnerabilities', 0)})</button>
                    <button class="severity-tab" onclick="showSeverityView('unique')">Unique Issues ({vuln_analysis.get('unique_count', 0)})</button>
                </div>
                
                <div id="total-severity" class="severity-grid">
        """
        for severity, count in total_severity_counts.items():
            color = severity_colors.get(severity, "#6c757d")
            html_content += f"""
                    <div class="severity-card">
                        <div class="severity-badge" style="background-color: {color};">{severity}</div>
                        <div style="font-size: 20px; font-weight: bold; margin-top: 10px;">{count}</div>
                        <div style="font-size: 12px; color: #6c757d;">total occurrences</div>
                    </div>
            """
        html_content += """
                </div>
                
                <div id="unique-severity" class="severity-grid" style="display: none;">
        """
        for severity, count in unique_severity_counts.items():
            color = severity_colors.get(severity, "#6c757d")
            html_content += f"""
                    <div class="severity-card">
                        <div class="severity-badge" style="background-color: {color};">{severity}</div>
                        <div style="font-size: 20px; font-weight: bold; margin-top: 10px;">{count}</div>
                        <div style="font-size: 12px; color: #6c757d;">unique types</div>
                    </div>
            """
        html_content += """
                </div>
            </div>
        """
    
    # Add discovered URLs section (collapsible)
    if scan_data.get('discovered_urls'):
        html_content += f"""
            <button class="collapsible" onclick="toggleCollapsible(this)">
                📋 Discovered URLs ({len(scan_data['discovered_urls'])}) - Click to expand
            </button>
            <div class="collapsible-content" style="display: none;">
                <div class="url-list" style="margin: 0; border-radius: 0;">
        """
        for url in scan_data['discovered_urls']:
            html_content += f'<div class="url-item">{safe_html_escape(url)}</div>'
        html_content += """
                </div>
            </div>
        """
    
    # Add results section with unique vulnerabilities
    html_content += '<div class="results-section"><h2>Detailed Results</h2>'
    
    # Show unique vulnerabilities by default
    unique_results = vuln_analysis.get('unique_results', [])
    if unique_results:
        html_content += f'''
            <div style="background: #e3f2fd; padding: 15px; border-radius: 8px; margin-bottom: 20px; border-left: 4px solid #2196f3;">
                <h4 style="margin: 0 0 10px 0; color: #1976d2;">📊 Showing Unique Vulnerabilities</h4>
                <p style="margin: 0; font-size: 14px; color: #666;">
                    Displaying {len(unique_results)} unique vulnerability types. Each may affect multiple URLs.
                    <button onclick="toggleResultView()" id="toggleViewBtn" style="margin-left: 15px; padding: 5px 10px; background: #2196f3; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 12px;">
                        Show All Occurrences ({scan_data.get('total_vulnerabilities', 0)})
                    </button>
                </p>
            </div>
        '''
        
        # Unique results view
        html_content += '<div id="unique-results">'
        for i, result in enumerate(unique_results):
            severity = safe_html_escape(result.get('severity', 'Unknown'))
            result_type = safe_html_escape(result.get('type', 'Unknown Issue'))
            result_url = safe_html_escape(result.get('url', 'N/A'))
            color = severity_colors.get(result.get('severity', 'Unknown'), "#6c757d")
            affected_urls = result.get('affected_urls', [result.get('url', 'N/A')])
            affected_count = len(affected_urls)
            
            html_content += f"""
                <div class="result-item" data-url="{result_url}" id="unique-result-{i}" style="border-left-color: {color};">
                    <div class="result-header">
                        <h3 style="margin: 0;">{result_type} <span class="url-count-badge">{affected_count} page{"s" if affected_count != 1 else ""}</span></h3>
                        <span class="severity-badge" style="background-color: {color};">{severity}</span>
                    </div>
                    <div class="result-body">
            """
            
            # Add description if available (safely escaped)
            if result.get('description'):
                safe_description = safe_html_escape(result['description'])
                html_content += f'<p><strong>Description:</strong> {safe_description}</p>'
            
            # Add affected URLs
            if len(affected_urls) > 1:
                html_content += f"""
                        <div class="affected-urls">
                            <h4>Affected URLs ({len(affected_urls)}):</h4>
                """
                for url in affected_urls:
                    html_content += f'<div class="url-item">{safe_html_escape(url)}</div>'
                html_content += '</div>'
            else:
                html_content += f'<p><strong>URL:</strong> {safe_html_escape(affected_urls[0])}</p>'
            
            # Add error if available (safely escaped)
            if result.get('error'):
                safe_error = safe_html_escape(result['error'])
                html_content += f'<p><strong>Error:</strong> {safe_error}</p>'
            
            # Add any other fields (safely escaped)
            for key, value in result.items():
                if key not in ['type', 'url', 'severity', 'description', 'error', 'affected_urls', 'affected_urls_count']:
                    safe_key = safe_html_escape(key.title())
                    safe_value = safe_html_escape(value)
                    html_content += f'<p><strong>{safe_key}:</strong> {safe_value}</p>'
            
            html_content += """
                    </div>
                </div>
            """
        html_content += '</div>'
        
        # All results view (hidden by default)
        html_content += '<div id="all-results" style="display: none;">'
        for i, result in enumerate(scan_data.get('results', [])):
            severity = safe_html_escape(result.get('severity', 'Unknown'))
            result_type = safe_html_escape(result.get('type', 'Unknown Issue'))
            result_url = safe_html_escape(result.get('url', 'N/A'))
            color = severity_colors.get(result.get('severity', 'Unknown'), "#6c757d")
            
            html_content += f"""
                <div class="result-item" data-url="{result_url}" id="all-result-{i}" style="border-left-color: {color};">
                    <div class="result-header">
                        <h3 style="margin: 0;">{result_type}</h3>
                        <span class="severity-badge" style="background-color: {color};">{severity}</span>
                    </div>
                    <div class="result-body">
                        <p><strong>URL:</strong> {result_url}</p>
            """
            
            # Add description if available (safely escaped)
            if result.get('description'):
                safe_description = safe_html_escape(result['description'])
                html_content += f'<p><strong>Description:</strong> {safe_description}</p>'
            
            # Add error if available (safely escaped)
            if result.get('error'):
                safe_error = safe_html_escape(result['error'])
                html_content += f'<p><strong>Error:</strong> {safe_error}</p>'
            
            # Add any other fields (safely escaped)
            for key, value in result.items():
                if key not in ['type', 'url', 'severity', 'description', 'error']:
                    safe_key = safe_html_escape(key.title())
                    safe_value = safe_html_escape(value)
                    html_content += f'<p><strong>{safe_key}:</strong> {safe_value}</p>'
            
            html_content += """
                    </div>
                </div>
            """
        html_content += '</div>'
    else:
        html_content += '<div class="no-results">No security issues found!</div>'
    
    # Add JavaScript for filtering and view switching functionality
    html_content += """
            </div>
        </div>
        
        <script>
            let currentView = 'unique';
            
            function filterResults() {
                const filterValue = document.getElementById('pageFilter').value;
                const resultSelector = currentView === 'unique' ? '#unique-results .result-item' : '#all-results .result-item';
                const resultItems = document.querySelectorAll(resultSelector);
                let visibleCount = 0;
                
                resultItems.forEach(item => {
                    const itemUrl = item.getAttribute('data-url');
                    
                    if (filterValue === 'all' || itemUrl === filterValue) {
                        item.style.display = 'block';
                        item.classList.remove('hidden');
                        visibleCount++;
                    } else {
                        item.style.display = 'none';
                        item.classList.add('hidden');
                    }
                });
                
                // Update stats
                document.getElementById('visibleResults').textContent = visibleCount;
                
                // Show message if no results for selected page
                const noResultsDiv = document.querySelector('.no-results');
                if (visibleCount === 0 && filterValue !== 'all') {
                    if (!document.getElementById('filtered-no-results')) {
                        const filteredNoResults = document.createElement('div');
                        filteredNoResults.id = 'filtered-no-results';
                        filteredNoResults.className = 'no-results';
                        filteredNoResults.innerHTML = '🔍 No security issues found for the selected page.';
                        document.querySelector('.results-section').appendChild(filteredNoResults);
                    }
                    document.getElementById('filtered-no-results').style.display = 'block';
                } else {
                    const filteredNoResults = document.getElementById('filtered-no-results');
                    if (filteredNoResults) {
                        filteredNoResults.style.display = 'none';
                    }
                }
            }
            
            function toggleResultView() {
                const uniqueResults = document.getElementById('unique-results');
                const allResults = document.getElementById('all-results');
                const toggleBtn = document.getElementById('toggleViewBtn');
                
                if (currentView === 'unique') {
                    uniqueResults.style.display = 'none';
                    allResults.style.display = 'block';
                    toggleBtn.textContent = 'Show Unique Issues';
                    currentView = 'all';
                } else {
                    uniqueResults.style.display = 'block';
                    allResults.style.display = 'none';
                    toggleBtn.textContent = 'Show All Occurrences';
                    currentView = 'unique';
                }
                
                // Re-apply current filter
                filterResults();
            }
            
            function showSeverityView(view) {
                const totalView = document.getElementById('total-severity');
                const uniqueView = document.getElementById('unique-severity');
                const tabs = document.querySelectorAll('.severity-tab');
                
                tabs.forEach(tab => tab.classList.remove('active'));
                
                if (view === 'total') {
                    totalView.style.display = 'grid';
                    uniqueView.style.display = 'none';
                    tabs[0].classList.add('active');
                } else {
                    totalView.style.display = 'none';
                    uniqueView.style.display = 'grid';
                    tabs[1].classList.add('active');
                }
            }
            
            function toggleCollapsible(element) {
                element.classList.toggle('active');
                const content = element.nextElementSibling;
                if (content.style.display === 'block') {
                    content.style.display = 'none';
                    element.innerHTML = element.innerHTML.replace('Click to collapse', 'Click to expand');
                } else {
                    content.style.display = 'block';
                    element.innerHTML = element.innerHTML.replace('Click to expand', 'Click to collapse');
                }
            }
            
            // Initialize filter on page load
            document.addEventListener('DOMContentLoaded', function() {
                filterResults();
            });
        </script>
    </body>
    </html>
    """
    
    return html_content

def save_scan_results(scan_data, target_url):
    """Save scan results to JSON and HTML files"""
    try:
        print(f"Starting to save scan results for: {target_url}")  # Debug log
        # Create results directory if it doesn't exist
        results_dir = "scan_results"
        os.makedirs(results_dir, exist_ok=True)
        print(f"Results directory created/verified: {results_dir}")  # Debug log
        
        # Generate filename based on target URL and timestamp
        parsed_url = urlparse(target_url)
        domain = parsed_url.netloc or parsed_url.path
        # Remove invalid characters for filename
        domain = "".join(c for c in domain if c.isalnum() or c in ('-', '_', '.'))
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_filename = f"{domain}_{timestamp}"
        
        # Add metadata to scan data
        scan_data_with_metadata = {
            "scan_metadata": {
                "timestamp": datetime.now().isoformat(),
                "target_url": target_url,
                "scan_type": "security_scan"
            },
            **scan_data
        }
        
        saved_files = {}
        
        # Save JSON file
        json_filename = f"{base_filename}.json"
        json_filepath = os.path.join(results_dir, json_filename)
        with open(json_filepath, 'w', encoding='utf-8') as f:
            json.dump(scan_data_with_metadata, f, indent=2, ensure_ascii=False)
        saved_files['json'] = json_filepath
        print(f"JSON file saved: {json_filepath}")  # Debug log
        
        # Save HTML file
        html_filename = f"{base_filename}.html"
        html_filepath = os.path.join(results_dir, html_filename)
        print(f"Generating HTML report...")  # Debug log
        html_content = generate_html_report(scan_data, target_url)
        print(f"HTML content generated, length: {len(html_content)} characters")  # Debug log
        with open(html_filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        saved_files['html'] = html_filepath
        print(f"HTML file saved: {html_filepath}")  # Debug log
        
        return saved_files
    except Exception as e:
        print(f"Error saving scan results: {str(e)}")  # Enhanced error logging
        import traceback
        traceback.print_exc()  # Print full traceback for debugging
        return None
