import json, re

input_file = "./cybersec_dataset_full.jsonl"
kept, removed = [], []

# Patterns de mauvaise qualité stricts
english_patterns = [
    "This guide", "In this guide", "Here are some", "Here is how",
    "Introduction", "Prerequisites:", "Steps to", "Note that",
    "For example,", "Additionally,", "However,", "It is important",
    "you can use", "you may want", "make sure",
]

incorrect_commands = [
    "find / -perm +4000",  # syntaxe incorrecte, doit être -4000
    "sudo -L",             # n'existe pas
    "nmap --unseen",       # n'existe pas
    "getstuff", "pypkatz.get", "kerberosgold",
    "sekurlsa::csv", "sekurlsa::minidump",
    "Rubeus.exe lsass::", "T1568.012",
    "getUserSPNs.py.*-requests",
    "hashcat.*kerberoS",
    "sudo -l --list-all",  # n'existe pas
    "bloodhound-postgresql", "dump_domains",
]

with open(input_file) as f:
    for line in f:
        try:
            ex = json.loads(line)
            content = " ".join([m["content"] for m in ex["messages"]])

            # Rejet strict : anglais dominant
            english_count = sum(1 for p in english_patterns if p.lower() in content.lower())
            has_incorrect = any(re.search(p, content, re.IGNORECASE) for p in incorrect_commands)

            # Rejet si beaucoup d'anglais OU commandes incorrectes
            if english_count >= 2 or has_incorrect:
                removed.append(line)
            else:
                kept.append(line)
        except:
            removed.append(line)

print(f"Gardés    : {len(kept)}")
print(f"Supprimés : {len(removed)}")
print(f"Taux de suppression : {len(removed)*100/(len(kept)+len(removed)):.0f}%")

# Sauvegarder
with open("./cybersec_dataset_clean_v3.jsonl", "w") as f:
    f.writelines(kept)

# Analyser un échantillon de supprimés pour valider
print("\n=== Exemples supprimés (5 premiers) ===")
for line in removed[:5]:
    ex = json.loads(line)
    print(f"Q: {ex['messages'][0]['content'][:80]}")
    print(f"R: {ex['messages'][1]['content'][:150]}")
    print("---")
