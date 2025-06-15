from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from scanner.headers import scan_security_headers
from scanner.injection import scan_injection
from scanner.ssrf import scan_ssrf
from scanner.crawler import crawl_domain
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import os
from datetime import datetime
from report import save_scan_results  # assumes this writes JSON + HTML into scan_results/

app = Flask(__name__)
CORS(app)

def scan_url(url):
    results = []
    try:
        header_results = scan_security_headers(url)
        injection_results = scan_injection(url)
        ssrf_results = scan_ssrf(url)
        results.extend(header_results + injection_results + ssrf_results)
    except Exception as e:
        results.append({
            "type": "Scan Error",
            "url": url,
            "error": str(e),
            "severity": "Low"
        })
    return results


def get_vulnerability_signature(result):
    """Generate a unique signature for a vulnerability based on type and description."""
    vuln_type = result.get("type", "")
    description = result.get("description", "")
    return f"{vuln_type}|{description}".lower().strip()


def analyze_vulnerabilities(all_results):
    """Analyze vulnerabilities to get total, unique counts and other statistics."""
    total_count = len(all_results)
    unique_vulns = {}
    affected_urls_per_vuln = {}

    for result in all_results:
        signature = get_vulnerability_signature(result)
        url = result.get("url", "Unknown URL")

        if signature not in unique_vulns:
            unique_vulns[signature] = result.copy()
            affected_urls_per_vuln[signature] = set()

        affected_urls_per_vuln[signature].add(url)

    unique_results = []
    for signature, vuln in unique_vulns.items():
        vuln_copy = vuln.copy()
        affected_urls = list(affected_urls_per_vuln[signature])
        vuln_copy["affected_urls"] = affected_urls
        vuln_copy["affected_urls_count"] = len(affected_urls)
        unique_results.append(vuln_copy)

    total_severity_counts = {}
    unique_severity_counts = {}

    for result in all_results:
        sev = result.get("severity", "Unknown")
        total_severity_counts[sev] = total_severity_counts.get(sev, 0) + 1

    for result in unique_results:
        sev = result.get("severity", "Unknown")
        unique_severity_counts[sev] = unique_severity_counts.get(sev, 0) + 1

    return {
        "total_count": total_count,
        "unique_count": len(unique_results),
        "unique_results": unique_results,
        "total_severity_counts": total_severity_counts,
        "unique_severity_counts": unique_severity_counts,
        "affected_urls_per_vuln": {
            sig: list(urls) for sig, urls in affected_urls_per_vuln.items()
        },
    }


@app.route("/scan", methods=["POST"])
def scan():
    """
    Receive JSON { "url": "<target_url>" }. 
    Perform the scan in parallel. 
    Return the scan_data JSON—no files are written.
    """
    data = request.get_json()
    target_url = data.get("url")

    if not target_url:
        return jsonify({"error": "No URL provided"}), 400

    crawled_urls = crawl_domain(target_url)
    all_results = []

    # Scan in parallel
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(scan_url, url): url for url in crawled_urls}
        for future in as_completed(futures):
            url = futures[future]
            try:
                results = future.result()
                all_results.extend(results)
            except Exception as e:
                all_results.append({
                    "type": "Scan Error",
                    "url": url,
                    "error": str(e),
                    "severity": "Low"
                })

    vuln_analysis = analyze_vulnerabilities(all_results)

    scan_data = {
        "target": target_url,
        "discovered_urls": crawled_urls,
        "total_vulnerabilities": len(all_results),
        "unique_vulnerabilities": vuln_analysis["unique_count"],
        "vulnerability_analysis": vuln_analysis,
        "results": all_results,
    }

    return jsonify(scan_data)


@app.route("/download/html", methods=["POST"])
def download_html():
    """
    Accept a POST with JSON body: { "scan_data": <the full scan_data JSON> }.
    Use save_scan_results(...) to generate an HTML file in scan_results/.
    Then immediately read that HTML file and return it as an attachment.
    """
    data = request.get_json()
    scan_data = data.get("scan_data", None)

    if not scan_data:
        return jsonify({"error": "No scan_data provided"}), 400

    # The 'target' field is used by save_scan_results to name files
    target_url = scan_data.get("target", "report")
    try:
        # This will create two files: a JSON and an HTML under scan_results/
        saved_files = save_scan_results(scan_data, target_url)
        # saved_files is typically a dict like:
        # { "json": "scan_results/<something>.json", "html": "scan_results/<something>.html" }
        html_path = saved_files.get("html", None)
        if not html_path or not os.path.exists(html_path):
            return jsonify({"error": "Failed to generate HTML report"}), 500

        # Stream the HTML file back with a Content-Disposition header so the browser downloads it
        filename = os.path.basename(html_path)
        return send_file(
            html_path,
            mimetype="text/html",
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        return jsonify({"error": f"Error generating HTML report: {str(e)}"}), 500


if __name__ == "__main__":
    # Ensure the scan_results directory exists (save_scan_results will write here)
    os.makedirs("scan_results", exist_ok=True)
    app.run(debug=True)
