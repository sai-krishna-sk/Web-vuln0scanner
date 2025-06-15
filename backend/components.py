import html
from datetime import datetime
from urllib.parse import urlparse

def safe_html_escape(text):
    """Safely escape HTML content to prevent XSS in reports"""
    if text is None:
        return "N/A"
    return html.escape(str(text), quote=True)

def get_vulnerability_signature(result):
    """Generate a unique signature for a vulnerability based on type and description"""
    vuln_type = result.get('type', '')
    description = result.get('description', '')
    return f"{vuln_type}|{description}".lower().strip()

def analyze_vulnerabilities(all_results):
    """Analyze vulnerabilities to get total, unique counts and other statistics"""
    total_count = len(all_results)
    
    unique_vulns = {}
    affected_urls_per_vuln = {}
    
    for result in all_results:
        signature = get_vulnerability_signature(result)
        url = result.get('url', 'Unknown URL')
        
        if signature not in unique_vulns:
            unique_vulns[signature] = result.copy()
            affected_urls_per_vuln[signature] = set()
        
        affected_urls_per_vuln[signature].add(url)
    
    unique_results = []
    for signature, vuln in unique_vulns.items():
        vuln_copy = vuln.copy()
        affected_urls = list(affected_urls_per_vuln[signature])
        vuln_copy['affected_urls'] = affected_urls
        vuln_copy['affected_urls_count'] = len(affected_urls)
        unique_results.append(vuln_copy)
    
    total_severity_counts = {}
    unique_severity_counts = {}
    
    for result in all_results:
        severity = result.get('severity', 'Unknown')
        total_severity_counts[severity] = total_severity_counts.get(severity, 0) + 1
    
    for result in unique_results:
        severity = result.get('severity', 'Unknown')
        unique_severity_counts[severity] = unique_severity_counts.get(severity, 0) + 1
    
    return {
        'total_count': total_count,
        'unique_count': len(unique_results),
        'unique_results': unique_results,
        'total_severity_counts': total_severity_counts,
        'unique_severity_counts': unique_severity_counts,
        'affected_urls_per_vuln': {sig: list(urls) for sig, urls in affected_urls_per_vuln.items()}
    }