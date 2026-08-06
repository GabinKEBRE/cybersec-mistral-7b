import json, re

input_file = "./cybersec_dataset_full.jsonl"
output_file = "./cybersec_dataset_clean_v2.jsonl"

# Patterns d'hallucinations connues à purger
bad_patterns = [
    # Outils inventés
    "pypkatz.get_user_spns", "getSTuff.py", "getstuff", "kerberosgold",
    "get_tgt_as_realm", "crackmapexec kerberos", "Get-DomainUser -Hashes",
    "getuserspns /domain_name", "pypkatz.get", "rubeus.exe lsass::mimikatz",
    "msfvenom.*kerberos_golden", "psexec.py -u.*-p.*-c",
    # Commandes inventées
    "GetUserSPNs.py.*-requests -show-target-names",
    "Rubeus.exe lsass::", "hashcat.*kerberoS",
    "john --wordlist-path", "john --wordlist=.*\.pot",
    # Réponses génériques sans commandes
    "In this guide, we will demonstrate",
    "This guide will explain how to use",
    "Ensure you have the latest version",
    "Run the following commands as a user with administrative",
    "Mathieu Gouerin", "Gentilkiwi",  # description erronée de mimikatz
    # TTP IDs incorrects
    "T1568.012", "T1558.012",
    # Commandes nmap incorrectes
    "nmap --unseen", "nmap -sL 192.168.*ports",
    # Commandes smb incorrectes  
    "nmap.*Update the Nmap database",
]

# Indicateurs de mauvaise qualité
quality_issues = [
    lambda c: len(c) < 200,  # trop court
    lambda c: c.count("```") < 2,  # pas de blocs de code
    lambda c: "Introduction" in c and "guide" in c.lower() and "```" not in c[:200],  # format générique sans code rapide
]

kept, removed_bad, removed_quality = 0, 0, 0

with open(input_file) as fin, open(output_file, "w") as fout:
    for line in fin:
        try:
            ex = json.loads(line)
            content = " ".join([m["content"] for m in ex["messages"]])
            answer = ex["messages"][1]["content"] if len(ex["messages"]) > 1 else ""

            # Vérifier les patterns d'hallucinations
            has_bad = any(
                re.search(p, content, re.IGNORECASE) for p in bad_patterns
            )
            if has_bad:
                removed_bad += 1
                continue

            # Vérifier la qualité minimale
            has_quality_issue = any(check(answer) for check in quality_issues)
            if has_quality_issue:
                removed_quality += 1
                continue

            fout.write(line)
            kept += 1
        except:
            pass

print(f"Gardés    : {kept}")
print(f"Hallucinations supprimées : {removed_bad}")
print(f"Qualité insuffisante      : {removed_quality}")
print(f"Total supprimé : {removed_bad + removed_quality}")
