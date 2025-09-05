"""
Interface Streamlit pour le générateur de redirections 301 avec scraping automatique
"""

import streamlit as st
import csv
import io
import os
from generator import RedirectGenerator
from scraper import crawl_site_with_fallback, WebScraper, parse_sitemap
from language_detector import LanguageDetector
from ai_mapper import AIMapper, AIMatchingError
from fallback_manager import FallbackManager

# Configuration de la page
st.set_page_config(
    page_title="301 Redirect Generator",
    page_icon="🦎",
    layout="wide"
)

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

def main():
    """Interface principale avec IA sémantique et support multilangue"""
    
    # Titre
    st.title("🦎 301 Redirect Generator")
    st.markdown("**Sprint 2** - IA sémantique GPT-3.5 + Support multilangue + Fallbacks 302")
    st.markdown("---")
    
    # Sélection du mode
    mode = st.radio(
        "🔧 Mode de génération",
        ["🚀 Mode IA (Sprint 2)", "🔄 Mode classique"],
        horizontal=True
    )
    
    if mode == "🚀 Mode IA (Sprint 2)":
        from advanced_interface import interface_ai_avancee
        interface_ai_avancee()
    else:
        from advanced_interface import interface_classique
        interface_classique()


def interface_classique_legacy():
    """Interface classique historique (conservée pour référence)"""
    
    # Interface simplifiée avec sitemap pour le nouveau site
    st.header("🔄 Collecte des URLs")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔗 Ancien site (en ligne)")
        
        # URL pour scraping
        old_site_url = st.text_input(
            label="URL ancien site",
            placeholder="https://ancien-site.com",
            key="old_url_input",
            help="L'outil va automatiquement explorer ce site pour trouver toutes les pages"
        )
        
        # Bouton de scraping
        scrape_old_button = st.button("⚡ Scraper l'ancien site", key="scrape_old", use_container_width=True, type="primary")
    
    with col2:
        st.subheader("🎯 Nouveau site (préproduction)")
        
        # URL du sitemap Yoast
        new_sitemap_url = st.text_input(
            label="URL du sitemap du nouveau site",
            placeholder="https://nouveau-site.com/sitemap_index.xml",
            key="new_sitemap_input",
            help="Entrez l'URL du sitemap XML (ex: /sitemap.xml ou /sitemap_index.xml)"
        )
        
        # Suggestion automatique
        st.info("💡 URLs courantes : `/sitemap.xml`, `/sitemap_index.xml`, `/wp-sitemap.xml`")
        
        # Bouton pour parser le sitemap
        parse_sitemap_button = st.button("📄 Parser le sitemap", key="parse_sitemap", use_container_width=True, type="primary")
    
    # Variables de session pour stocker les résultats
    if 'scraped_old_urls' not in st.session_state:
        st.session_state.scraped_old_urls = []
    if 'parsed_new_urls' not in st.session_state:
        st.session_state.parsed_new_urls = []
    if 'old_scraping_success' not in st.session_state:
        st.session_state.old_scraping_success = False
    if 'new_parsing_success' not in st.session_state:
        st.session_state.new_parsing_success = False
    
    # Traitement du scraping de l'ancien site
    if scrape_old_button:
        if not old_site_url.strip():
            st.error("❌ Veuillez saisir l'URL de l'ancien site avant de lancer le scraping.")
        else:
            with st.spinner("🔍 Scraping de l'ancien site en cours..."):
                old_urls, old_success = crawl_site_with_fallback(old_site_url, max_pages=1000)
                
                st.session_state.scraped_old_urls = old_urls
                st.session_state.old_scraping_success = old_success
                
                if old_success:
                    st.success(f"✅ Ancien site scrapé avec succès ! Trouvé {len(old_urls)} pages.")
                else:
                    st.error(f"❌ Impossible de scraper l'ancien site : {old_site_url}")
                    st.info("💡 Utilisez la saisie manuelle ci-dessous pour l'ancien site.")
    
    # Traitement du parsing du sitemap pour le nouveau site
    if parse_sitemap_button:
        if not new_sitemap_url.strip():
            st.error("❌ Veuillez saisir l'URL du sitemap avant de lancer le parsing.")
        else:
            with st.spinner("🔍 Parsing du sitemap en cours..."):
                # Parse le sitemap
                new_urls = parse_sitemap(new_sitemap_url, recursive=True)
                
                if new_urls:
                    # Convertir en URLs relatives pour le nouveau site
                    from urllib.parse import urlparse
                    parsed_urls = []
                    for url in new_urls:
                        parsed = urlparse(url)
                        path = parsed.path
                        if not path:
                            path = '/'
                        parsed_urls.append(path)
                    
                    st.session_state.parsed_new_urls = parsed_urls
                    st.session_state.new_parsing_success = True
                    
                    st.success(f"✅ Sitemap parsé avec succès ! Trouvé {len(parsed_urls)} URLs.")
                else:
                    st.session_state.parsed_new_urls = []
                    st.session_state.new_parsing_success = False
                    st.error(f"❌ Impossible de parser le sitemap : {new_sitemap_url}")
                    st.info("💡 Vérifiez l'URL du sitemap ou utilisez le mode manuel ci-dessous.")
    
    # Logique de génération des redirections
    st.markdown("---")
    st.subheader("🎯 Génération des redirections")
    
    # Détermine les URLs finales
    final_old_urls = st.session_state.scraped_old_urls if st.session_state.old_scraping_success else []
    final_new_urls = st.session_state.parsed_new_urls if st.session_state.new_parsing_success else []
    
    old_source = "scraping" if final_old_urls else "aucun"
    new_source = "sitemap" if final_new_urls else "aucun"
    
    # Affichage du statut
    col_status1, col_status2 = st.columns(2)
    
    with col_status1:
        if final_old_urls:
            st.success(f"✅ Ancien site : {len(final_old_urls)} URLs ({old_source})")
        else:
            st.warning("⚠️ Ancien site : Aucune URL (scrapez ou saisissez manuellement)")
    
    with col_status2:
        if final_new_urls:
            st.success(f"✅ Nouveau site : {len(final_new_urls)} URLs ({new_source})")
        else:
            st.warning("⚠️ Nouveau site : Aucune URL (scrapez ou saisissez manuellement)")
    
    # Bouton de génération si on a les deux listes
    if final_old_urls and final_new_urls:
        
        # Aperçu des URLs
        with st.expander("👁️ Aperçu des URLs détectées"):
            display_url_preview(final_old_urls, final_new_urls)
        
        # Vérification de correspondance
        if len(final_old_urls) != len(final_new_urls):
            st.warning(f"⚠️ Nombre d'URLs différent : {len(final_old_urls)} vs {len(final_new_urls)}. Les redirections seront générées pour les URLs correspondantes.")
        
        # Bouton de génération
        col_gen1, col_gen2, col_gen3 = st.columns([1, 1, 1])
        with col_gen2:
            generate_button = st.button("🚀 Générer les redirections", use_container_width=True, type="primary")
        
        if generate_button:
            htaccess_content, csv_data, error = generate_redirections_from_lists(
                final_old_urls, 
                final_new_urls
            )
            
            if error:
                st.error(f"❌ Erreur lors de la génération: {error}")
            else:
                # Affichage des résultats
                st.success(f"✅ {len(csv_data)-1} redirections générées avec succès !")
                
                # Aperçu du .htaccess
                st.subheader("📄 Aperçu du fichier .htaccess")
                st.code(htaccess_content, language="apache")
                
                # Boutons de téléchargement
                st.markdown("---")
                st.subheader("📥 Téléchargements")
                
                col_dl1, col_dl2 = st.columns(2)
                
                with col_dl1:
                    st.download_button(
                        label="⬇️ Télécharger .htaccess",
                        data=htaccess_content,
                        file_name="redirections.htaccess",
                        mime="text/plain"
                    )
                
                with col_dl2:
                    # Génération du CSV
                    csv_buffer = io.StringIO()
                    csv_writer = csv.writer(csv_buffer)
                    csv_writer.writerows(csv_data)
                    csv_content = csv_buffer.getvalue()
                    
                    st.download_button(
                        label="⬇️ Télécharger CSV",
                        data=csv_content,
                        file_name="redirections_audit.csv",
                        mime="text/csv"
                    )
                
                # Aperçu du CSV
                st.subheader("📊 Aperçu du fichier CSV")
                st.dataframe(csv_data[1:], column_config={
                    "0": "Ancienne URL complète",
                    "1": "Ancien chemin", 
                    "2": "Nouvelle URL complète",
                    "3": "Nouveau chemin"
                })
    else:
        st.info("💡 Scrapez ou saisissez manuellement les URLs des deux sites pour générer les redirections.")

    # Mode upload de fichiers (bonus)
    st.markdown("---")
    with st.expander("📁 Mode upload de fichiers (optionnel)"):
        st.markdown("**Uploadez directement vos fichiers sitemap.xml ou listes d'URLs**")
        
        col_up1, col_up2 = st.columns(2)
        
        with col_up1:
            st.subheader("📄 Fichier ancien site")
            old_file = st.file_uploader(
                "Fichier ancien site",
                type=['txt', 'xml'],
                help="Fichier texte ou sitemap.xml",
                key="old_file_upload"
            )
        
        with col_up2:
            st.subheader("📄 Fichier nouveau site")
            new_file = st.file_uploader(
                "Fichier nouveau site", 
                type=['txt', 'xml'],
                help="Fichier texte ou sitemap.xml",
                key="new_file_upload"
            )
        
        if old_file and new_file:
            if st.button("🚀 Générer depuis fichiers", key="generate_from_files"):
                try:
                    old_content = old_file.read().decode('utf-8')
                    new_content = new_file.read().decode('utf-8')
                    
                    generator = RedirectGenerator()
                    htaccess_content, csv_data = generator.generate_redirections(old_content, new_content)
                    
                    st.success(f"✅ {len(csv_data)-1} redirections générées depuis les fichiers !")
                    
                    # Interface de téléchargement
                    col_dl1, col_dl2 = st.columns(2)
                    
                    with col_dl1:
                        st.download_button(
                            label="⬇️ Télécharger .htaccess",
                            data=htaccess_content,
                            file_name="redirections.htaccess",
                            mime="text/plain",
                            key="download_htaccess_files"
                        )
                    
                    with col_dl2:
                        csv_buffer = io.StringIO()
                        csv_writer = csv.writer(csv_buffer)
                        csv_writer.writerows(csv_data)
                        csv_content = csv_buffer.getvalue()
                        
                        st.download_button(
                            label="⬇️ Télécharger CSV",
                            data=csv_content,
                            file_name="redirections_audit.csv",
                            mime="text/csv",
                            key="download_csv_files"
                        )
                    
                    # Aperçu du CSV
                    st.subheader("📊 Aperçu du fichier CSV")
                    st.dataframe(csv_data[1:])
                    
                except Exception as e:
                    st.error(f"❌ Erreur lors du traitement des fichiers: {str(e)}")

    # Mode manuel (fallback)
    st.markdown("---")
    with st.expander("🛠️ Mode manuel (si les méthodes automatiques échouent)"):
        st.markdown("**Saisie manuelle des URLs si besoin**")
        
        col1_manual, col2_manual = st.columns(2)
        
        with col1_manual:
            st.subheader("🔗 URLs anciennes")
            old_urls_manual = st.text_area(
                label="URLs anciennes (manuel)",
                placeholder="Collez vos anciennes URLs ici...\nExemple:\nhttps://ancien-site.com/page1\nhttps://ancien-site.com/page2",
                height=200,
                key="old_manual_input",
                help="Sitemap XML, liste brute ou CSV"
            )
        
        with col2_manual:
            st.subheader("🎯 URLs nouvelles") 
            new_urls_manual = st.text_area(
                label="URLs nouvelles (manuel)",
                placeholder="Collez vos nouvelles URLs ici...\nExemple:\nhttps://nouveau-site.com/page1\nhttps://nouveau-site.com/page2",
                height=200,
                key="new_manual_input",
                help="Sitemap XML, liste brute ou CSV"
            )
        
        if st.button("🚀 Générer depuis le mode manuel", key="generate_manual"):
            if old_urls_manual.strip() and new_urls_manual.strip():
                try:
                    generator = RedirectGenerator()
                    htaccess_content, csv_data = generator.generate_redirections(old_urls_manual, new_urls_manual)
                    
                    st.success(f"✅ {len(csv_data)-1} redirections générées avec succès !")
                    
                    # Affichage et téléchargements
                    col_dl1, col_dl2 = st.columns(2)
                    with col_dl1:
                        st.download_button(
                            label="⬇️ Télécharger .htaccess",
                            data=htaccess_content,
                            file_name="redirections.htaccess",
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
                    
                except Exception as e:
                    st.error(f"❌ Erreur: {str(e)}")
            else:
                st.error("❌ Veuillez remplir les deux champs.")
    
    # Instructions d'utilisation
    with st.expander("📋 Instructions & aide"):
        st.markdown("""
        ### 🎯 Nouvelle stratégie optimisée
        
        #### 1️⃣ Ancien site (en ligne)
        - **Scraping automatique** : Entrez l'URL et cliquez "Scraper"
        - L'outil explore automatiquement jusqu'à 200 pages
        
        #### 2️⃣ Nouveau site (préproduction)
        - **Parsing du sitemap** : Entrez l'URL du sitemap XML
        - Compatible avec Yoast SEO et sitemaps standards
        - Parse récursivement les sitemaps index
        
        ### 💡 Pourquoi cette approche ?
        - **Ancien site** : Scraping car il est public et accessible
        - **Nouveau site** : Sitemap car souvent bloqué (robots.txt, noindex, auth)
        
        ### 🔍 Où trouver le sitemap ?
        URLs courantes :
        - `/sitemap.xml`
        - `/sitemap_index.xml`
        - `/wp-sitemap.xml` (WordPress)
        - Consultez `/robots.txt` pour trouver le sitemap
        
        ### ⚠️ Dépannage
        - **Scraping échoue** → Utilisez le mode manuel
        - **Sitemap introuvable** → Demandez à l'intégrateur
        - **Nombre d'URLs différent** → Normal, matching adaptatif
        """)
    
    # Instructions pour les deux modes
    with st.expander("📋 Instructions & aide"):
        st.markdown("""
        ### 🚀 Mode IA (Sprint 2) - Recommandé
        
        #### ✨ Fonctionnalités avancées
        - **IA sémantique GPT-3.5** : Matching intelligent des URLs par similarité sémantique
        - **Support multilangue** : Détection automatique et traitement par langue
        - **Fallbacks 302** : Redirections temporaires pour langues non migrées
        - **Contexte métier** : Améliore le matching avec vos spécifications projet
        
        #### 🔧 Configuration IA
        - **Température** : Créativité de l'IA (0.0 = conservateur, 1.0 = créatif)
        - **Seuil de confiance** : Score minimum pour valider une correspondance
        - **Taille des lots** : URLs traitées simultanément (impact sur coût API)
        
        ### 🔄 Mode classique
        - Mapping alphabétique traditionnel
        - Sans IA, sans analyse linguistique
        - Compatible avec l'ancien workflow
        
        ### 💡 Recommandations
        - **Nouveau projet** → Mode IA pour matching précis
        - **Site multilingue** → Mode IA obligatoire 
        - **Budget limité** → Mode classique acceptable
        """)
    
    # Footer
    st.markdown("---")
    st.markdown("*Développé pour SEPTEO Digital Services — Fire Salamander Team* 🦎")
    st.markdown("*v4.0 - Sprint 2 avec IA sémantique et support multilangue*")

if __name__ == "__main__":
    main()