"""
Interface Streamlit pour le générateur de redirections 301 avec scraping automatique
"""

import streamlit as st
import csv
import io
from generator import RedirectGenerator
from scraper import crawl_site_with_fallback, WebScraper

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
    """Interface principale avec scraping automatique"""
    
    # Titre
    st.title("🦎 301 Redirect Generator")
    st.markdown("**Mode automatique avec scraping intelligent** - Entrez 2 URLs, obtenez vos redirections !")
    st.markdown("---")

    # Mode par défaut : Scraping automatique
    st.header("🔄 Mode automatique (recommandé)")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔗 URL ancien site")
        old_site_url = st.text_input(
            label="URL ancien site",
            placeholder="https://ancien-site.com",
            label_visibility="collapsed",
            help="L'outil va automatiquement explorer ce site pour trouver toutes les pages"
        )
    
    with col2:
        st.subheader("🎯 URL nouveau site") 
        new_site_url = st.text_input(
            label="URL nouveau site",
            placeholder="https://nouveau-site.com",
            label_visibility="collapsed", 
            help="L'outil va automatiquement explorer ce site pour trouver toutes les pages"
        )
    
    # Bouton de scraping
    st.markdown("")
    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
    with col_btn2:
        scrape_button = st.button("⚡ Scraper les deux sites", use_container_width=True, type="primary")
    
    # Variables de session pour stocker les résultats
    if 'scraped_old_urls' not in st.session_state:
        st.session_state.scraped_old_urls = []
    if 'scraped_new_urls' not in st.session_state:
        st.session_state.scraped_new_urls = []
    if 'scraping_success' not in st.session_state:
        st.session_state.scraping_success = False
    
    # Traitement du scraping
    if scrape_button:
        if not old_site_url.strip() or not new_site_url.strip():
            st.error("❌ Veuillez saisir les deux URLs avant de lancer le scraping.")
        else:
            with st.spinner("🔍 Scraping en cours... Cela peut prendre quelques secondes"):
                
                # Scraping de l'ancien site
                st.info("📡 Scraping de l'ancien site...")
                old_urls, old_success = crawl_site_with_fallback(old_site_url, max_pages=200)
                
                # Scraping du nouveau site  
                st.info("📡 Scraping du nouveau site...")
                scraper = WebScraper()
                new_urls_absolute, new_success = crawl_site_with_fallback(new_site_url, max_pages=200)
                
                # Convertit les nouvelles URLs en relatives
                new_urls = []
                if new_success and new_urls_absolute:
                    new_urls = scraper.crawl_site_relative(new_site_url, max_pages=200)
                    if not new_urls:
                        new_success = False
                
                # Stocke les résultats
                st.session_state.scraped_old_urls = old_urls
                st.session_state.scraped_new_urls = new_urls
                st.session_state.scraping_success = old_success and new_success
                
                # Affiche les résultats du scraping
                if st.session_state.scraping_success:
                    st.success(f"✅ Scraping réussi ! Trouvé {len(old_urls)} pages sur l'ancien site et {len(new_urls)} sur le nouveau.")
                else:
                    st.warning("⚠️ Le scraping automatique a échoué ou n'a pas trouvé d'URLs. Utilisez le mode manuel ci-dessous.")
                    if not old_success:
                        st.error(f"❌ Impossible de scraper l'ancien site : {old_site_url}")
                    if not new_success:
                        st.error(f"❌ Impossible de scraper le nouveau site : {new_site_url}")
    
    # Affichage des résultats du scraping si disponibles
    if st.session_state.scraped_old_urls or st.session_state.scraped_new_urls:
        st.markdown("---")
        st.subheader("👁️ Aperçu des URLs détectées")
        
        display_url_preview(st.session_state.scraped_old_urls, st.session_state.scraped_new_urls)
        
        # Vérification de correspondance
        if len(st.session_state.scraped_old_urls) != len(st.session_state.scraped_new_urls):
            st.warning(f"⚠️ Nombre d'URLs différent : {len(st.session_state.scraped_old_urls)} vs {len(st.session_state.scraped_new_urls)}. Les redirections seront générées pour les URLs correspondantes.")
        
        # Bouton de génération des redirections
        col_gen1, col_gen2, col_gen3 = st.columns([1, 1, 1])
        with col_gen2:
            generate_from_scraping = st.button("🚀 Générer les redirections", use_container_width=True, type="primary")
        
        if generate_from_scraping:
            if st.session_state.scraped_old_urls and st.session_state.scraped_new_urls:
                htaccess_content, csv_data, error = generate_redirections_from_lists(
                    st.session_state.scraped_old_urls, 
                    st.session_state.scraped_new_urls
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
                st.error("❌ Aucune URL trouvée pour générer les redirections.")

    # Mode manuel (fallback)
    st.markdown("---")
    with st.expander("🛠️ Mode manuel (si le scraping automatique ne fonctionne pas)"):
        st.markdown("**Utilisez ce mode si :**")
        st.markdown("- Le scraping automatique a échoué")
        st.markdown("- Vous préférez coller vos listes d'URLs manuellement")
        st.markdown("- Vous avez des fichiers sitemap.xml à uploader")
        
        # Tabs pour les différents modes manuels
        tab1, tab2 = st.tabs(["📝 Copier-coller", "📁 Upload fichiers"])
        
        with tab1:
            col1_manual, col2_manual = st.columns(2)
            
            with col1_manual:
                st.subheader("🔗 Anciennes URLs")
                old_urls_manual = st.text_area(
                    label="Anciennes URLs",
                    placeholder="Collez ici vos anciennes URLs...\nExemple:\nhttps://ancien-site.com/page1\nhttps://ancien-site.com/page2",
                    height=300,
                    label_visibility="collapsed",
                    help="Formats supportés: sitemap XML, liste brute, CSV"
                )
            
            with col2_manual:
                st.subheader("🎯 Nouvelles URLs") 
                new_urls_manual = st.text_area(
                    label="Nouvelles URLs",
                    placeholder="Collez ici vos nouvelles URLs...\nExemple:\nhttps://nouveau-site.com/nouvelle-page1\nhttps://nouveau-site.com/nouvelle-page2",
                    height=300,
                    label_visibility="collapsed",
                    help="Formats supportés: sitemap XML, liste brute, CSV"
                )
            
            # Bouton de génération manuelle
            col_manual1, col_manual2, col_manual3 = st.columns([1, 1, 1])
            with col_manual2:
                generate_manual = st.button("🚀 Générer (mode manuel)", use_container_width=True)
            
            if generate_manual:
                if not old_urls_manual.strip() or not new_urls_manual.strip():
                    st.error("❌ Veuillez remplir les deux champs avant de générer les redirections.")
                else:
                    try:
                        generator = RedirectGenerator()
                        htaccess_content, csv_data = generator.generate_redirections(old_urls_manual, new_urls_manual)
                        
                        # Affichage des résultats (même code que plus haut)
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
                        st.dataframe(csv_data[1:])
                        
                    except ValueError as e:
                        st.error(f"❌ Erreur de correspondance: {str(e)}")
                        st.info("💡 Vérifiez que vous avez le même nombre d'URLs dans les deux listes.")
                    except Exception as e:
                        st.error(f"❌ Erreur lors de la génération: {str(e)}")
        
        with tab2:
            st.subheader("📁 Upload de fichiers")
            col_up1, col_up2 = st.columns(2)
            
            with col_up1:
                old_file = st.file_uploader(
                    "Fichier ancien site",
                    type=['txt', 'xml'],
                    help="Fichier texte ou sitemap.xml"
                )
            
            with col_up2:
                new_file = st.file_uploader(
                    "Fichier nouveau site", 
                    type=['txt', 'xml'],
                    help="Fichier texte ou sitemap.xml"
                )
            
            if old_file and new_file:
                if st.button("🚀 Générer depuis fichiers"):
                    try:
                        old_content = old_file.read().decode('utf-8')
                        new_content = new_file.read().decode('utf-8')
                        
                        generator = RedirectGenerator()
                        htaccess_content, csv_data = generator.generate_redirections(old_content, new_content)
                        
                        st.success(f"✅ {len(csv_data)-1} redirections générées depuis les fichiers !")
                        
                        # Interface de téléchargement (même code que plus haut)
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
                            csv_content = csv_buffer.getvalue()
                            
                            st.download_button(
                                label="⬇️ Télécharger CSV",
                                data=csv_content,
                                file_name="redirections_audit.csv",
                                mime="text/csv"
                            )
                        
                    except Exception as e:
                        st.error(f"❌ Erreur lors du traitement des fichiers: {str(e)}")

    # Instructions d'utilisation
    with st.expander("📋 Instructions & aide"):
        st.markdown("""
        ### 🔄 Mode automatique (recommandé)
        1. **Entrez l'URL de l'ancien site** (ex: https://ancien-site.com)
        2. **Entrez l'URL du nouveau site** (ex: https://nouveau-site.com)
        3. **Cliquez sur "Scraper les deux sites"** - L'outil va automatiquement explorer jusqu'à 200 pages de chaque site
        4. **Vérifiez les URLs détectées** dans l'aperçu
        5. **Générez les redirections** et téléchargez vos fichiers
        
        ### 🛠️ Mode manuel (fallback)
        Utilisez ce mode si le scraping automatique échoue :
        - **Copier-coller** : Collez vos listes d'URLs ou contenus de sitemap
        - **Upload** : Importez vos fichiers sitemap.xml ou listes d'URLs
        
        ### 📤 Formats supportés
        - Sitemap XML (balises `<loc>`)
        - Liste brute (une URL par ligne)
        - CSV copié (deux colonnes)
        
        ### ⚠️ Dépannage
        - Si le scraping échoue : vérifiez que les sites sont accessibles
        - En cas de blocage robots.txt : utilisez le mode manuel
        - Pour des sites avec authentification : contactez l'équipe technique
        """)
    
    # Footer
    st.markdown("---")
    st.markdown("*Développé pour SEPTEO Digital Services — Fire Salamander Team* 🦎")
    st.markdown("*v2.0 avec scraping automatique intelligent*")

if __name__ == "__main__":
    main()