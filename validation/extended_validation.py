import requests, json

API = "http://localhost:8000/v1/query"
HEADERS = {"Authorization": "Bearer demo-key-gabin-2024", "Content-Type": "application/json"}

extended_tests = [
    # Cloud
    {"q": "AWS S3 bucket enumeration et exploitation",
     "must_contain": ["aws s3", "bucket"],
     "must_not_contain": ["In this guide"]},
    {"q": "Kubernetes pod escape techniques",
     "must_contain": ["kubectl", "privileged"],
     "must_not_contain": ["This guide"]},
    {"q": "Azure AD device code flow attack",
     "must_contain": ["oauth", "azure"],
     "must_not_contain": ["This guide"]},
    # Web avancé
    {"q": "SSRF exploitation vers AWS metadata IMDS",
     "must_contain": ["169.254.169.254", "metadata"],
     "must_not_contain": ["In this guide"]},
    {"q": "JWT alg=none attack exploitation",
     "must_contain": ["jwt", "alg"],
     "must_not_contain": ["In this guide"]},
    {"q": "GraphQL introspection query attack",
     "must_contain": ["graphql", "__schema"],
     "must_not_contain": ["This guide"]},
    # Windows avancé
    {"q": "PrintNightmare CVE-2021-1675 exploitation",
     "must_contain": ["printnightmare", "spooler"],
     "must_not_contain": ["This guide"]},
    {"q": "ZeroLogon CVE-2020-1472 exploitation",
     "must_contain": ["zerologon", "netlogon"],
     "must_not_contain": ["This guide"]},
    # Forensics
    {"q": "Volatility 3 analyse dump mémoire Windows",
     "must_contain": ["vol.py", "windows.pslist"],
     "must_not_contain": ["This guide"]},
    # OSINT
    {"q": "Subdomain enumeration avec amass et subfinder",
     "must_contain": ["amass", "subfinder"],
     "must_not_contain": ["This guide"]},
    # Défense
    {"q": "Splunk SIEM détection Kerberoasting",
     "must_contain": ["splunk", "4769"],
     "must_not_contain": ["This guide"]},
    # Reporting
    {"q": "Rédiger un rapport pentest avec CVSS v3.1",
     "must_contain": ["cvss", "cwe"],
     "must_not_contain": ["This guide"]},
]

def test_query(q):
    try:
        r = requests.post(API, headers=HEADERS,
            json={"question": q, "max_tokens": 500, "temperature": 0.3}, timeout=60)
        return r.json()["answer"] if r.status_code == 200 else None
    except:
        return None

passed = 0
print("=" * 65)
print("VALIDATION ÉTENDUE — Sujets avancés")
print("=" * 65)

for i, t in enumerate(extended_tests):
    results = []
    for _ in range(3):
        answer = test_query(t["q"])
        if answer is None:
            results.append(False)
            continue
        answer_lower = answer.lower()
        ok_req = all(kw.lower() in answer_lower for kw in t["must_contain"])
        ok_forb = all(kw.lower() not in answer_lower for kw in t["must_not_contain"])
        results.append(ok_req and ok_forb)

    pass_count = sum(results)
    status = "✓ PASS" if pass_count >= 2 else "✗ FAIL"
    print(f"[{i+1:2}] {status} ({pass_count}/3) — {t['q'][:55]}")
    if pass_count >= 2:
        passed += 1

print("=" * 65)
print(f"Résultat étendu : {passed}/{len(extended_tests)} = {passed*100//len(extended_tests)}%")
