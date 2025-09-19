# 🔥🐍 Fire Snake 301

**v1.2.0** - Générateur de redirections 301 avec IA sémantique

Générez vos redirections 301 intelligemment avec l'IA.  
📦 Pas besoin de coder. 🧠 L'IA comprend vos URLs.  
🚀 Collez n'importe quel format d'URLs et obtenez un `.htaccess` prêt pour production.

---

## 🎯 Objectif

Outil professionnel pour chefs de projet, intégrateurs et responsables SEO.  
Automatise la génération des redirections 301/302 entre un **ancien site** et un **nouveau site** après une refonte.

> 🧠 **Nouveauté v1.2.0** : IA sémantique + Parser universel  
> 👉 **L'IA comprend le sens de vos URLs pour un matching intelligent.**

---

## ✨ Fonctionnalités v1.2.0

### 🧠 **IA Sémantique**
- **Matching intelligent** avec GPT-3.5-turbo
- **Compréhension multilingue** automatique  
- **Contexte métier** pour optimiser les correspondances
- **Fallback 302** intelligent vers pages d'accueil

### 🎯 **Input Universel** 
- **Auto-détection de format** : XML, JSON, CSV, Text
- **Sitemap XML** avec namespaces et sous-sitemaps
- **JSON Arrays** modernes
- **CSV avec headers** automatiquement détectés
- **Nettoyage automatique** des espaces et caractères parasites

### 🚀 **Crawler Intelligent**
- **Headers HTTP adaptatifs** (7 User-Agents en rotation)
- **Retry automatique** avec backoff exponentiel
- **Contournement Cloudflare** et protection anti-bot
- **Gestion rate limiting** (header Retry-After)

### 📄 **Génération**
- **Fichier .htaccess** avec URLs absolues
- **Export CSV** détaillé avec confidences
- **Export Excel** format Balt (Septeo CMS)
- **Commentaires IA** expliquant chaque redirection

---

## 🚀 Démarrage rapide

### Installation

```bash
git clone https://github.com/jeromegonz1/301-redirect-generator.git
cd 301-redirect-generator
python -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

### Configuration

```bash
# Créer le fichier .env
echo "OPENAI_API_KEY=your-openai-api-key" > .env
```

### Lancement

```bash
streamlit run app.py
```

L'application sera disponible sur **http://localhost:8501**

### Test avec Input Universel

1. Sélectionnez **"Input universel"** dans l'interface
2. Collez votre sitemap XML, JSON, CSV ou liste d'URLs  
3. L'IA détecte automatiquement le format
4. Obtenez vos redirections 301/302 intelligentes !

---

## 📂 Structure du projet



/fire-snake-301
├── src/
│ ├── main.py ← Interface Streamlit
│ └── generator.py ← Logique de parsing / génération
├── tests/
│ └── test_generator.py ← Tests TDD
├── outputs/ ← Fichiers générés
├── requirements.txt
├── CDC.md
├── README.md


---

## 🚀 Lancer le projet (dev local)

```bash
# Installer les dépendances
pip install -r requirements.txt

# Lancer l'app
streamlit run src/main.py

🧪 Lancer les tests
pytest tests/



🔒 Contraintes techniques

🚫 Interdiction de hardcoder des URLs

✅ Développement en TDD

✅ 100% Open Source et minimaliste

🏁 Déploiement recommandé

Replit (dev rapide)

Streamlit Cloud (prod public)

Railway.app (auto-deploy GitHub + domaine personnalisé)



---

## 🤝 Contribuer

Vous avez une idée d'amélioration ?  
Un bug à signaler ?  
👉 Ouvrez une issue ou une pull request !  
Nous utilisons une méthodologie TDD stricte et refusons le hardcoding.

---

## 🧙‍♂️ Auteur

Développé par [Jérôme Gonzalez](https://github.com/jeromegonz1)  
Pour SEPTEO Digital Services — Fire Salamander Team
