import requests

# Expanded headers list from your JSON report
SECURITY_HEADERS = {
    "Content-Security-Policy": "Prevents XSS attacks",
    "X-Content-Type-Options": "Prevents MIME-type sniffing",
    "X-Frame-Options": "Protects against clickjacking",
    "Strict-Transport-Security": "Enforces HTTPS",
    "Referrer-Policy": "Controls how much referrer info is shared",
    "X-Permitted-Cross-Domain-Policies": "Cross-domain policy control",
    "X-XSS-Protection": "XSS protection"
}

# Headers indicating information disclosure
INFO_DISCLOSURE_HEADERS = {
    "Server": "Server header reveals server information",
    "X-Powered-By": "X-Powered-By header reveals server information"
}

def scan_security_headers(url):
    try:
        r = requests.get(url, timeout=10)
        headers = r.headers
        findings = []

        # Check for missing security headers
        for header, description in SECURITY_HEADERS.items():
            if header not in headers:
                findings.append({
                    "type": "Missing Security Header",
                    "header": header,
                    "description": description,
                    "severity": "Medium",
                    "location": "HTTP Response Headers",
                    "url": url,
                    "payload": f"Missing: {header}",
                    "evidence": f"{header} header not present - {description}"
                })

        # Check for information disclosure headers
        for header, description in INFO_DISCLOSURE_HEADERS.items():
            if header in headers:
                findings.append({
                    "type": "Information Disclosure",
                    "header": header,
                    "description": description,
                    "severity": "Low",
                    "location": f"{header} header",
                    "url": url,
                    "payload": f"{header}: {headers[header]}",
                    "evidence": description
                })

        return findings
    except Exception as e:
        return [{"error": f"Failed to fetch URL: {str(e)}"}]
