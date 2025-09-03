📄 README.md – Présentation & Instructions
# 🦎 301 Redirect Generator

Générez vos redirections 301 en un clic.  
📦 Pas besoin de coder. 🧠 Pas besoin de réfléchir.  
🚀 Copiez vos anciennes et nouvelles URLs, et obtenez un `.htaccess` prêt à coller sur votre serveur.

---

## 🎯 Objectif

Cet outil est conçu pour les chefs de projet, intégrateurs ou responsables SEO.  
Il automatise la génération des redirections 301 entre un **ancien site** et un **nouveau site** après une refonte.

> 🧠 Toute la magie réside dans le gain de temps offert.  
> 👉 **Vous ne faites que copier-coller vos URLs.**

---

## ✅ Fonctionnalités

- 🔸 Accepte :
  - Sitemap XML (balises `<loc>`)
  - Liste brute d’URLs (une par ligne)
  - CSV collé (deux colonnes)

- 🔸 Génère automatiquement :
  - Un fichier `.htaccess` :
    ```
    Redirect 301 https://ancien-site.com/page /nouvelle-page
    ```
  - Un fichier `.csv` d’audit avec :
    ```
    OLD_FULL_URL, OLD_PATH, NEW_FULL_URL, NEW_PATH
    ```

- 🔸 Interface super simple :
  - Deux zones de texte
  - Bouton "Générer"
  - Aperçu des résultats
  - Boutons de téléchargement

---

## 📂 Structure du projet



/301-redirect-generator
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
