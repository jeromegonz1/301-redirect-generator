# Cahier des Charges – 301‑Redirect‑Generator

## 1. Contexte & Objectif
L’outil permet de générer automatiquement des redirections 301 entre deux sites (site A → site B), à partir de leurs sitemaps. Il doit être **ultra simple**, utilisable depuis Replit ou tout environnement local.

## 2. Contraintes techniques
- **INTERDIT LE HARDCODING** : aucune URL fixe dans le code. Tout doit être dynamique via inputs utilisateur.
- **METHODE TDD OBLIGATOIRE** : tout comportement doit être préalablement défini par un test Pytest, exécuté en CI.
- **Versionning Git dès le départ**.

## 3. Stack technique (V1)
- Langage : **Python 3.x**
- CLI simple ou interface web légère (ex. **Streamlit**)
- Tests : **Pytest**
- Export : `.htaccess` et `.csv`

## 4. Fonctionnalités attendues – V1
1. Input : deux champs (`sitemap_old`, `sitemap_new`) en copier-coller (texte brut ou XML).
2. Normalisation des URLs : suppression domaine, trailing slash, etc.
3. Matching **ligne par ligne** entre les deux listes d’URL.
4. Génération dynamique de deux fichiers exportables :
   - `redirects.csv` — colonnes : `old_url,new_url`
   - `.htaccess` — lignes format Apache : `Redirect 301 /ancienne /nouvelle`
5. Logs ou message utilisateur indiquant les URLs sans correspondance.

## 5. Workflow de développement TDD
- Définir un test Pytest pour chaque fonctionnalité listée.
- Implémenter le code minimal pour passer le test.
- Ajouter un commit `feat: feature X via TDD`.

## 6. CI / automatisation (GitHub Actions)
- Configurer une action GitHub qui exécute les tests à chaque push/PR.

## 7. Roadmap potentielle – V2 (post‑MVP)
- Matching flou (similarité Levenshtein ou slug diff)
- Interface de revue manuelle
- Export JSON/YAML pour intégration BALT
- Vérification des URLs HTTP (200/404)
