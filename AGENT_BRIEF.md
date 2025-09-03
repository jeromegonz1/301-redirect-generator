AGENT_BRIEF.md – Prompt qualité pour Replit (à copier-coller)
Tu es un agent développeur expert. Tu travailles sous la direction d'un cadre produit.

🎯 Ton objectif :
Développer un outil appelé **301 Redirect Generator**, permettant de générer un fichier `.htaccess` et un `.csv` de redirections 301 à partir de deux listes d'URLs (copiées depuis un ancien et un nouveau site).

---

🛠️ TON CADRE DE TRAVAIL (À RESPECTER STRICTEMENT) :

1. 🎯 **Aucune URL ne doit être codée en dur**
   - Tu dois tout traiter à partir des inputs utilisateur
   - Tu n'écris **aucune valeur d'URL statique**

2. ✅ **Méthodologie TDD obligatoire**
   - Écris les tests dans `tests/test_generator.py` **avant** ou **pendant** le dev de chaque fonction
   - Utilise `pytest` pour tout valider

3. 🧱 **Structure du projet attendue**
   - `/src/generator.py` → logique principale
   - `/src/main.py` → interface Streamlit
   - `/outputs/` → `.htaccess` + `.csv`
   - `/tests/test_generator.py` → tests unitaires

4. 📥 **Format d'entrée utilisateur :**
   - Copié-collé de sitemap XML (balises `<loc>`)
   - Ou liste brute d'URLs (1 par ligne)
   - Ou CSV brut (ancienne, nouvelle URL)

5. 📤 **Format de sortie `.htaccess` :**
   ```apache
   Redirect 301 https://ancien-site.com/page /nouvelle-page
   ```
   - Ancienne URL complète
   - Nouvelle URL relative

6. 📤 **Format de sortie `.csv` :**
   ```
   OLD_FULL_URL, OLD_PATH, NEW_FULL_URL, NEW_PATH
   ```

---

💬 **INSTRUCTIONS SUPPLÉMENTAIRES :**

- Tu dois écrire un code modulaire, commenté, et facile à maintenir
- Tu commences par coder les fonctions utiles (parser, matcher, générateur)
- Tu relies ensuite ces fonctions à l'interface Streamlit dans main.py
- Tu testes chaque fonction indépendamment
- Tu commits avec des messages clairs : feat:, test:, fix:, etc.

🔥 **Ton but** : livrer un outil fonctionnel, testé, propre, prêt à être déployé.

Tu peux commencer par coder dans `/src/generator.py` les fonctions suivantes :
- `parse_input()`
- `match_urls()`
- `generate_htaccess()`
- `generate_csv()`

Tu peux ensuite les tester avec Pytest et les brancher sur le bouton de main.py.

Bonne chance.

---

✅ Tu peux enregistrer ce prompt dans un fichier `AGENT_BRIEF.md` à la racine du projet.  
🧙 Et l'envoyer tel quel à Replit ou Claude pour qu'il *comprenne le niveau d'exigence* et code dans le **cadre que toi et moi avons posé**.