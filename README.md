# 🛡️ CyberSec Mistral 7B — Fine-tuning d'un LLM pour la Cybersécurité Offensive

[![HuggingFace](https://img.shields.io/badge/🤗-Model-yellow)](https://huggingface.co/gabinkebre/cybersec-mistral-7b)
[![Score](https://img.shields.io/badge/Validation-8%2F8-brightgreen)]()
[![Loss](https://img.shields.io/badge/Loss-0.299-blue)]()
[![License](https://img.shields.io/badge/License-Apache--2.0-orange)]()

> **Projet de fine-tuning de Mistral-7B pour créer un assistant IA spécialisé en cybersécurité offensive (pentest, red team, audit), déployé comme SaaS complet avec API et interface web.**

## 🎯 Aperçu du projet

Ce projet démontre un pipeline complet de fine-tuning d'un LLM :
- **Modèle** : Mistral-7B-Instruct fine-tuné avec QLoRA 4-bit
- **Framework** : Unsloth (2x plus rapide)
- **Dataset** : 1269 exemples cybersécurité en français, curatés manuellement
- **Infrastructure** : Serveur GPU NVIDIA RTX 4000 Ada 21GB
- **Déploiement** : API FastAPI + Nginx + Interface web SaaS
- **Résultat** : **100% de validation** sur 8 sujets critiques

## 📸 Screenshots

### Interface SaaS
![Interface CyberSec AI](./screenshots/interface.png)

### Exemple de réponse
![Exemple de réponse](./screenshots/response.png)

## 🏗️ Architecture technique

## 🔐 Configuration des tokens

Avant d'utiliser les scripts, définir la variable d'environnement HuggingFace :

```bash
export HF_TOKEN="votre_token_huggingface"
```

Obtenir un token : https://huggingface.co/settings/tokens
