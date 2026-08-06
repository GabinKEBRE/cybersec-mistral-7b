import requests, json

API = "http://localhost:8000/v1/query"
HEADERS = {"Authorization": "Bearer demo-key-gabin-2024", "Content-Type": "application/json"}

tests = [
    {"q": "Kerberoasting : commandes GetUserSPNs et hashcat exactes",
     "must_contain": ["GetUserSPNs", "hashcat", "-m 13100"],
     "must_not_contain": ["pypkatz", "getSTuff", "kerberosgold"]},
    {"q": "Comment utiliser impacket-psexec avec un hash NTLM ?",
     "must_contain": ["impacket-psexec", "-hashes"],
     "must_not_contain": ["psexec.py -u"]},
    {"q": "Commandes mimikatz pour dumper LSASS",
     "must_contain": ["privilege::debug"],
     "must_not_contain": ["sekurlsa::csv", "sekurlsa::minidump"]},
    {"q": "Commandes nmap pour scanner les vulnérabilités SMB",
     "must_contain": ["nmap", "smb-vuln"],
     "must_not_contain": ["--unseen"]},
    {"q": "SQL injection UNION-based avec sqlmap",
     "must_contain": ["sqlmap", "--dbs"],
     "must_not_contain": ["In this guide", "This guide"]},
    {"q": "Comment bypasser AMSI sous PowerShell ?",
     "must_contain": ["iUtils", "[Ref].Assembly"],
     "must_not_contain": ["ModSecurity"]},
    {"q": "Techniques de privilege escalation Linux avec les commandes",
     "must_contain": ["find / -perm -4000", "sudo -l", "linpeas"],
     "must_not_contain": ["This guide", "In this guide"]},
    {"q": "BloodHound-python commandes pour collecter les données AD",
     "must_contain": ["bloodhound-python", "-c All", "domain.local"],
     "must_not_contain": ["run_bloodhound", "collect_data"]},
]

def test_query(q):
    try:
        r = requests.post(API, headers=HEADERS,
            json={"question": q, "max_tokens": 500, "temperature": 0.3}, timeout=60)
        if r.status_code != 200:
            return None
        return r.json()["answer"]
    except:
        return None

passed = 0
print("=" * 65)
for i, t in enumerate(tests):
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
    print(f"[{i+1}] {status} ({pass_count}/3) — {t['q'][:55]}")
    if pass_count >= 2:
        passed += 1

print("=" * 65)
print(f"Résultat : {passed}/{len(tests)} = {passed*100//len(tests)}%")
