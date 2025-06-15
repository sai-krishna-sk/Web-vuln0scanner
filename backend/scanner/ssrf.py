# scanner/ssrf.py
import requests
import concurrent.futures
from urllib.parse import urlparse, urljoin

HEADERS = {
    "User-Agent": "Mozilla/5.0 (VulnScanner)"
}

# Common SSRF payloads (metadata, localhost, etc.)
SSRF_PAYLOADS = [
    "http://127.0.0.1", "http://localhost", "http://169.254.169.254",
    "http://0.0.0.0", "http://[::1]", "http://169.254.169.254/latest/meta-data/",
    "http://internal.example.com", "http://localhost:80/admin"
]

# Parameters often vulnerable to SSRF
COMMON_PARAM_NAMES = [
    "url", "uri", "path", "target", "dest", "redirect", "next", "data", "resource"
]


def test_ssrf(target_url, param, payload):
    session = requests.Session()
    session.headers.update(HEADERS)
    try:
        r = session.get(target_url, params={param: payload}, timeout=10, allow_redirects=True)
        lower_body = r.text.lower()

        if any(indicator in lower_body for indicator in ["meta-data", "hostname", "root:x", "127.0.0.1", "localhost"]):
            return {
                "type": "SSRF",
                "url": r.url,
                "parameter": param,
                "payload": payload,
                "status_code": r.status_code,
                "severity": "High",
                "description": f"Potential SSRF via parameter '{param}' using payload '{payload}'"
            }

    except requests.exceptions.RequestException as e:
        print(f"[!] SSRF test failed on {target_url} with param '{param}' and payload '{payload}': {e}")
    finally:
        session.close()

    return None



def scan_ssrf(target_url):
    print(f"[*] Starting SSRF scan on: {target_url}")
    results = []
    futures = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        for param in COMMON_PARAM_NAMES:
            for payload in SSRF_PAYLOADS:
                futures.append(executor.submit(test_ssrf, target_url, param, payload))

        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if result:
                print(f"[+] SSRF vulnerability found: {result}")
                results.append(result)

    return results
