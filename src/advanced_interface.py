"""
Interface avancée Sprint 2 avec IA sémantique et support multilangue
"""

import streamlit as st
import csv
import io
import os
from typing import List, Dict, Any
from generator import RedirectGenerator
from scraper import crawl_site_with_fallback, WebScraper, parse_sitemap
from language_detector import LanguageDetector
from ai_mapper import AIMapper, AIMatchingError
from fallback_manager import FallbackManager


def interface_ai_avancee():
    """Interface avancée avec IA sémantique et multilangue"""
    
    st.header("🚀 Générateur IA avec support multilangue")
    st.info("ℹ️ Cette interface utilise GPT-3.5-turbo pour le matching sémantique intelligent des URLs")
    
    # Vérification de la clé API
    if not os.getenv("OPENAI_API_KEY"):
        st.error("❌ Clé API OpenAI manquante. Veuillez la configurer dans les secrets Replit.")
        return
    
    # Configuration IA
    with st.expander("⚙️ Configuration IA"):
        col1, col2 = st.columns(2)
        with col1:
            temperature = st.slider("🌡️ Température IA", 0.0, 1.0, 0.1, 0.1,
                                   help="0.0 = conservateur, 1.0 = créatif")
            chunk_size = st.number_input("📦 Taille des lots", 10, 50, 20,
                                       help="URLs traitées par lot")
        with col2:
            confidence_threshold = st.slider("🎯 Seuil de confiance", 0.5, 0.9, 0.7, 0.05,
                                            help="Score minimum pour valider un match")
            fallback_lang = st.selectbox("🌐 Langue de fallback", 
                                       ["fr", "en", "de", "es", "it", "nl"], 
                                       index=0)
    
    # Collecte des URLs
    st.header("📊 Collecte des URLs")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔗 Ancien site")
        old_input_mode = st.radio("Mode", ["URL à scraper", "Liste manuelle"], key="old")
        
        if old_input_mode == "URL à scraper":
            old_url = st.text_input("URL de l'ancien site", placeholder="https://ancien-site.com")
            if st.button("🕷️ Scraper ancien site"):
                if old_url:
                    with st.spinner("Scraping en cours..."):
                        old_urls = crawl_site_with_fallback(old_url, max_pages=200)
                        st.session_state.old_urls = old_urls
                        st.success(f"✅ {len(old_urls)} URLs collectées")
                else:
                    st.error("Veuillez entrer une URL")
        else:
            old_text = st.text_area("URLs (une par ligne)", height=200, key="old_manual")
            if old_text:
                st.session_state.old_urls = [url.strip() for url in old_text.split('\n') if url.strip()]
    
    with col2:
        st.subheader("🎯 Nouveau site")
        new_input_mode = st.radio("Mode", ["Sitemap XML", "Liste manuelle"], key="new")
        
        if new_input_mode == "Sitemap XML":
            sitemap_url = st.text_input("URL du sitemap", placeholder="https://nouveau-site.com/sitemap.xml")
            if st.button("🗺️ Parser sitemap"):
                if sitemap_url:
                    with st.spinner("Parsing du sitemap..."):
                        new_urls = parse_sitemap(sitemap_url)
                        st.session_state.new_urls = new_urls
                        st.success(f"✅ {len(new_urls)} URLs extraites")
                else:
                    st.error("Veuillez entrer une URL de sitemap")
        else:
            new_text = st.text_area("URLs (une par ligne)", height=200, key="new_manual")
            if new_text:
                st.session_state.new_urls = [url.strip() for url in new_text.split('\n') if url.strip()]
    
    # Affichage des URLs collectées avec analyse linguistique
    if hasattr(st.session_state, 'old_urls') and hasattr(st.session_state, 'new_urls'):
        old_urls = st.session_state.old_urls
        new_urls = st.session_state.new_urls
        
        st.header("🔍 Analyse multilangue")
        
        # Détection des langues
        detector = LanguageDetector()
        old_grouped = detector.group_by_language(old_urls)
        new_grouped = detector.group_by_language(new_urls)
        
        # Affichage de l'analyse
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("📊 Total ancien", len(old_urls))
            st.metric("🌐 Langues ancien", len(old_grouped))
            
        with col2:
            st.metric("📊 Total nouveau", len(new_urls))
            st.metric("🌐 Langues nouveau", len(new_grouped))
            
        with col3:
            # Calcul des langues manquantes
            fallback_manager = FallbackManager(fallback_lang)
            missing_langs = fallback_manager.detect_missing_languages(old_urls, new_urls)
            st.metric("⚠️ Langues manquantes", len(missing_langs))
            if missing_langs:
                st.warning(f"Langues non migrées: {', '.join(missing_langs)}")
        
        # Détails par langue
        with st.expander("📈 Détails par langue"):
            all_langs = set(old_grouped.keys()) | set(new_grouped.keys())
            
            for lang in sorted(all_langs):
                old_count = len(old_grouped.get(lang, []))
                new_count = len(new_grouped.get(lang, []))
                status = "✅ Migrée" if new_count > 0 else "❌ Manquante"
                
                st.write(f"**{lang.upper()}** - Ancien: {old_count}, Nouveau: {new_count} - {status}")
        
        # Configuration du contexte métier
        st.header("💼 Contexte métier (optionnel)")
        contexte_metier = st.text_area(
            "Informations pour améliorer le matching IA",
            placeholder="""Exemple:
- Refonte complète avec nouvelle arborescence
- Section 'Actualités' devient 'Blog'  
- Produits regroupés par catégories
- URLs en français uniquement sur nouveau site""",
            height=100
        )
        
        # Génération avec IA
        if st.button("🤖 Générer avec IA sémantique", type="primary"):
            with st.spinner("🧠 IA en cours de traitement..."):
                try:
                    # Initialisation de l'IA
                    ai_mapper = AIMapper(
                        api_key=os.getenv("OPENAI_API_KEY"),
                        temperature=temperature,
                        chunk_size=chunk_size
                    )
                    
                    # Génération du rapport de fallback d'abord
                    if missing_langs:
                        st.subheader("📋 Rapport des redirections temporaires")
                        fallback_report = fallback_manager.generate_fallback_report(old_urls, new_urls)
                        st.text(fallback_report)
                    
                    # Matching IA pour chaque langue commune
                    st.subheader("🤖 Résultats du matching IA")
                    
                    all_matches = []
                    all_unmatched = []
                    
                    common_langs = set(old_grouped.keys()) & set(new_grouped.keys())
                    
                    for lang in sorted(common_langs):
                        if old_grouped[lang] and new_grouped[lang]:
                            st.write(f"**🔄 Traitement langue: {lang.upper()}**")
                            
                            # Matching IA pour cette langue
                            result = ai_mapper.match_urls(
                                old_grouped[lang],
                                new_grouped[lang],
                                contexte_metier=contexte_metier,
                                langue=lang
                            )
                            
                            # Affichage des résultats
                            matches = result.correspondances
                            unmatched = result.non_matchees
                            
                            st.success(f"✅ {len(matches)} correspondances trouvées")
                            if unmatched:
                                st.warning(f"⚠️ {len(unmatched)} URLs non matchées")
                            
                            # Filtre par confiance
                            filtered_matches = [
                                match for match in matches 
                                if match.get('confidence', 0) >= confidence_threshold
                            ]
                            
                            if len(filtered_matches) < len(matches):
                                excluded = len(matches) - len(filtered_matches)
                                st.info(f"🎯 {excluded} matches exclus (confiance < {confidence_threshold})")
                            
                            all_matches.extend(filtered_matches)
                            all_unmatched.extend(unmatched)
                    
                    # Génération des redirections 302 pour langues manquantes
                    redirects_302 = []
                    if missing_langs:
                        redirects_302 = fallback_manager.generate_302_redirects(
                            missing_langs, old_grouped, fallback_lang
                        )
                    
                    # Génération du fichier .htaccess final
                    st.subheader("📄 Fichier .htaccess généré")
                    
                    htaccess_lines = [
                        "# Redirections 301 générées par IA sémantique",
                        "# 301 Redirect Generator - Sprint 2",
                        ""
                    ]
                    
                    # Ajout des redirections 301 IA
                    if all_matches:
                        htaccess_lines.extend([
                            "# Redirections 301 - Matching IA sémantique",
                            ""
                        ])
                        
                        for match in all_matches:
                            source = match['ancienne']
                            target = match['nouvelle']
                            confidence = match.get('confidence', 0)
                            reason = match.get('raison', '')
                            
                            htaccess_lines.append(f"# {reason} (confiance: {confidence:.2f})")
                            htaccess_lines.append(f"Redirect 301 {source} {target}")
                            htaccess_lines.append("")
                    
                    # Ajout des redirections 302 pour fallbacks
                    if redirects_302:
                        fallback_htaccess = fallback_manager.format_htaccess_302(redirects_302)
                        htaccess_lines.extend([
                            "",
                            fallback_htaccess
                        ])
                    
                    htaccess_content = "\n".join(htaccess_lines)
                    
                    # Affichage et téléchargement
                    st.code(htaccess_content, language="apache")
                    
                    col_dl1, col_dl2, col_dl3 = st.columns(3)
                    
                    with col_dl1:
                        st.download_button(
                            label="⬇️ Télécharger .htaccess",
                            data=htaccess_content,
                            file_name="htaccess_ai_semantic.txt",
                            mime="text/plain"
                        )
                    
                    with col_dl2:
                        # Génération du CSV détaillé
                        csv_data = [["Source", "Target", "Type", "Confidence", "Reason", "Language"]]
                        
                        # Ajout des matches IA
                        for match in all_matches:
                            csv_data.append([
                                match['ancienne'],
                                match['nouvelle'], 
                                "301",
                                f"{match.get('confidence', 0):.2f}",
                                match.get('raison', ''),
                                detector.detect(match['ancienne'])
                            ])
                        
                        # Ajout des fallbacks 302
                        for source, target in redirects_302:
                            csv_data.append([
                                source,
                                target,
                                "302",
                                "N/A",
                                "Langue non migrée",
                                detector.detect(source)
                            ])
                        
                        csv_buffer = io.StringIO()
                        csv_writer = csv.writer(csv_buffer)
                        csv_writer.writerows(csv_data)
                        
                        st.download_button(
                            label="⬇️ Télécharger CSV",
                            data=csv_buffer.getvalue(),
                            file_name="redirections_ai_detailed.csv",
                            mime="text/csv"
                        )
                    
                    with col_dl3:
                        # Statistiques détaillées
                        stats = {
                            "total_301": len(all_matches),
                            "total_302": len(redirects_302),
                            "unmatched": len(all_unmatched),
                            "languages_processed": len(common_langs),
                            "missing_languages": len(missing_langs)
                        }
                        
                        st.metric("📊 Stats", f"301: {stats['total_301']} | 302: {stats['total_302']}")
                        
                        if all_unmatched:
                            with st.expander("⚠️ URLs non matchées"):
                                for url in all_unmatched:
                                    st.text(url)
                
                except AIMatchingError as e:
                    st.error(f"❌ Erreur IA: {str(e)}")
                except Exception as e:
                    st.error(f"❌ Erreur inattendue: {str(e)}")


def interface_classique():
    """Interface classique sans IA (pour compatibilité)"""
    
    st.header("🔄 Mode classique (sans IA)")
    st.info("ℹ️ Mode traditionnel avec mapping alphabétique")
    
    # Interface simplifiée avec sitemap pour le nouveau site
    st.header("🔄 Collecte des URLs")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔗 Ancien site (en ligne)")
        
        # Option 1: Scraping automatique
        st.markdown("**Option 1: Scraping automatique**")
        old_url = st.text_input("URL de l'ancien site à scraper", placeholder="https://ancien-site.com")
        max_pages = st.number_input("Nombre max de pages", 50, 500, 200)
        
        if st.button("🕷️ Lancer le scraping"):
            if old_url:
                with st.spinner("Scraping en cours..."):
                    old_urls = crawl_site_with_fallback(old_url, max_pages=max_pages)
                    st.session_state.old_urls_scraped = old_urls
                    st.success(f"✅ {len(old_urls)} URLs scrapées avec succès!")
            else:
                st.error("❌ Veuillez entrer l'URL de l'ancien site.")
        
        # Option 2: Upload CSV/TXT
        st.markdown("**Option 2: Upload fichier**")
        old_file = st.file_uploader("Fichier URLs anciennes", type=['csv', 'txt'], key="old_file")
        
        # Option 3: Saisie manuelle
        st.markdown("**Option 3: Saisie manuelle**") 
        old_manual = st.text_area("URLs anciennes (une par ligne)", height=150, key="old_manual_classic")
        
    with col2:
        st.subheader("🎯 Nouveau site (préproduction)")
        
        # Option 1: Parsing sitemap XML
        st.markdown("**Option 1: Sitemap XML (recommandé)**")
        sitemap_url = st.text_input("URL du sitemap", placeholder="https://nouveau-site.com/sitemap.xml")
        
        if st.button("🗺️ Parser le sitemap"):
            if sitemap_url:
                with st.spinner("Parsing du sitemap..."):
                    new_urls = parse_sitemap(sitemap_url)
                    st.session_state.new_urls_sitemap = new_urls
                    st.success(f"✅ {len(new_urls)} URLs extraites du sitemap!")
            else:
                st.error("❌ Veuillez entrer l'URL du sitemap.")
        
        # Option 2: Upload CSV/TXT
        st.markdown("**Option 2: Upload fichier**")
        new_file = st.file_uploader("Fichier URLs nouvelles", type=['csv', 'txt'], key="new_file")
        
        # Option 3: Saisie manuelle
        st.markdown("**Option 3: Saisie manuelle**")
        new_manual = st.text_area("URLs nouvelles (une par ligne)", height=150, key="new_manual_classic")
    
    # Collecte finale des URLs
    old_urls = []
    new_urls = []
    
    # Anciennes URLs
    if hasattr(st.session_state, 'old_urls_scraped'):
        old_urls = st.session_state.old_urls_scraped
    elif old_file:
        content = old_file.read().decode()
        old_urls = [url.strip() for url in content.split('\n') if url.strip()]
    elif old_manual:
        old_urls = [url.strip() for url in old_manual.split('\n') if url.strip()]
    
    # Nouvelles URLs
    if hasattr(st.session_state, 'new_urls_sitemap'):
        new_urls = st.session_state.new_urls_sitemap
    elif new_file:
        content = new_file.read().decode()
        new_urls = [url.strip() for url in content.split('\n') if url.strip()]
    elif new_manual:
        new_urls = [url.strip() for url in new_manual.split('\n') if url.strip()]
    
    # Affichage des URLs collectées
    if old_urls and new_urls:
        display_url_preview(old_urls, new_urls)
        
        # Génération des redirections classiques
        if st.button("⚡ Générer les redirections", type="primary"):
            with st.spinner("Génération en cours..."):
                htaccess_content, csv_data, error = generate_redirections_from_lists(old_urls, new_urls)
                
                if error:
                    st.error(f"❌ Erreur: {error}")
                else:
                    st.success("✅ Redirections générées avec succès!")
                    
                    # Affichage du contenu .htaccess
                    st.subheader("📄 Contenu .htaccess")
                    st.code(htaccess_content, language="apache")
                    
                    # Boutons de téléchargement
                    col_dl1, col_dl2 = st.columns(2)
                    with col_dl1:
                        st.download_button(
                            label="⬇️ Télécharger .htaccess",
                            data=htaccess_content,
                            file_name="htaccess_redirections.txt",
                            mime="text/plain"
                        )
                    with col_dl2:
                        csv_buffer = io.StringIO()
                        csv_writer = csv.writer(csv_buffer)
                        csv_writer.writerows(csv_data)
                        st.download_button(
                            label="⬇️ Télécharger CSV",
                            data=csv_buffer.getvalue(),
                            file_name="redirections_audit.csv",
                            mime="text/csv"
                        )
    
    elif old_urls or new_urls:
        st.warning("⚠️ Veuillez fournir les URLs pour l'ancien ET le nouveau site.")


def display_url_preview(old_urls, new_urls):
    """Affiche un aperçu des URLs détectées"""
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader(f"🔗 Anciennes URLs détectées ({len(old_urls)})")
        if old_urls:
            # Affiche les 10 premières URLs
            preview_old = old_urls[:10]
            for url in preview_old:
                st.text(url)
            if len(old_urls) > 10:
                st.text(f"... et {len(old_urls) - 10} autres")
        else:
            st.warning("Aucune URL détectée")
    
    with col2:
        st.subheader(f"🎯 Nouvelles URLs détectées ({len(new_urls)})")
        if new_urls:
            # Affiche les 10 premières URLs
            preview_new = new_urls[:10]
            for url in preview_new:
                st.text(url)
            if len(new_urls) > 10:
                st.text(f"... et {len(new_urls) - 10} autres")
        else:
            st.warning("Aucune URL détectée")


def generate_redirections_from_lists(old_urls, new_urls):
    """Génère les redirections à partir de deux listes d'URLs"""
    try:
        generator = RedirectGenerator()
        
        # Convertit les listes en texte pour le générateur existant
        old_text = '\n'.join(old_urls)
        new_text = '\n'.join(new_urls)
        
        htaccess_content, csv_data = generator.generate_redirections(old_text, new_text)
        return htaccess_content, csv_data, None
        
    except Exception as e:
        return None, None, str(e)