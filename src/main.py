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
    """Interface principale avec scraping flexible"""
    
    # Titre
    st.title("🦎 301 Redirect Generator")
    st.markdown("**Mode flexible** - Scrapez automatiquement ou saisissez manuellement selon vos besoins !")
    st.markdown("---")

    # Interface hybride
    st.header("🔄 Mode hybride (scraping + manuel)")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔗 Ancien site")
        
        # URL pour scraping
        old_site_url = st.text_input(
            label="URL ancien site (pour scraping)",
            placeholder="https://ancien-site.com",
            key="old_url_input",
            help="URL pour scraping automatique"
        )
        
        # Bouton de scraping individuel
        scrape_old_button = st.button("📡 Scraper ancien site", key="scrape_old", use_container_width=True)
        
        st.markdown("**OU saisie manuelle :**")
        
        # Zone de saisie manuelle
        old_urls_manual = st.text_area(
            label="URLs anciennes (manuel)",
            placeholder="Collez vos anciennes URLs ici...\nExemple:\nhttps://ancien-site.com/page1\nhttps://ancien-site.com/page2",
            height=200,
            key="old_manual_input",
            help="Sitemap XML, liste brute ou CSV"
        )
    
    with col2:
        st.subheader("🎯 Nouveau site") 
        
        # URL pour scraping
        new_site_url = st.text_input(
            label="URL nouveau site (pour scraping)",
            placeholder="https://nouveau-site.com",
            key="new_url_input",
            help="URL pour scraping automatique"
        )
        
        # Bouton de scraping individuel
        scrape_new_button = st.button("📡 Scraper nouveau site", key="scrape_new", use_container_width=True)
        
        st.markdown("**OU saisie manuelle :**")
        
        # Zone de saisie manuelle
        new_urls_manual = st.text_area(
            label="URLs nouvelles (manuel)",
            placeholder="Collez vos nouvelles URLs ici...\nExemple:\nhttps://nouveau-site.com/page1\nhttps://nouveau-site.com/page2",
            height=200,
            key="new_manual_input",
            help="Sitemap XML, liste brute ou CSV"
        )
    
    # Variables de session pour stocker les résultats
    if 'scraped_old_urls' not in st.session_state:
        st.session_state.scraped_old_urls = []
    if 'scraped_new_urls' not in st.session_state:
        st.session_state.scraped_new_urls = []
    if 'old_scraping_success' not in st.session_state:
        st.session_state.old_scraping_success = False
    if 'new_scraping_success' not in st.session_state:
        st.session_state.new_scraping_success = False
    
    # Traitement du scraping de l'ancien site
    if scrape_old_button:
        if not old_site_url.strip():
            st.error("❌ Veuillez saisir l'URL de l'ancien site avant de lancer le scraping.")
        else:
            with st.spinner("🔍 Scraping de l'ancien site en cours..."):
                old_urls, old_success = crawl_site_with_fallback(old_site_url, max_pages=200)
                
                st.session_state.scraped_old_urls = old_urls
                st.session_state.old_scraping_success = old_success
                
                if old_success:
                    st.success(f"✅ Ancien site scrapé avec succès ! Trouvé {len(old_urls)} pages.")
                else:
                    st.error(f"❌ Impossible de scraper l'ancien site : {old_site_url}")
                    st.info("💡 Utilisez la saisie manuelle ci-dessous pour l'ancien site.")
    
    # Traitement du scraping du nouveau site
    if scrape_new_button:
        if not new_site_url.strip():
            st.error("❌ Veuillez saisir l'URL du nouveau site avant de lancer le scraping.")
        else:
            with st.spinner("🔍 Scraping du nouveau site en cours..."):
                scraper = WebScraper()
                new_urls = scraper.crawl_site_relative(new_site_url, max_pages=200)
                new_success = len(new_urls) > 0
                
                st.session_state.scraped_new_urls = new_urls
                st.session_state.new_scraping_success = new_success
                
                if new_success:
                    st.success(f"✅ Nouveau site scrapé avec succès ! Trouvé {len(new_urls)} pages.")
                else:
                    st.error(f"❌ Impossible de scraper le nouveau site : {new_site_url}")
                    st.info("💡 Utilisez la saisie manuelle ci-dessous pour le nouveau site.")
    
    # Logique de combinaison scraping/manuel et génération
    st.markdown("---")
    st.subheader("🎯 Génération des redirections")
    
    # Détermine les URLs finales (scraping + manuel)
    final_old_urls = []
    final_new_urls = []
    
    # Pour l'ancien site : priorité au scraping si disponible, sinon manuel
    if st.session_state.scraped_old_urls and st.session_state.old_scraping_success:
        final_old_urls = st.session_state.scraped_old_urls
        old_source = "scraping"
    elif old_urls_manual.strip():
        # Parse les URLs manuelles
        generator = RedirectGenerator()
        final_old_urls = generator.parse_urls(old_urls_manual)
        old_source = "manuel"
    else:
        old_source = "aucun"
    
    # Pour le nouveau site : priorité au scraping si disponible, sinon manuel
    if st.session_state.scraped_new_urls and st.session_state.new_scraping_success:
        final_new_urls = st.session_state.scraped_new_urls
        new_source = "scraping"
    elif new_urls_manual.strip():
        # Parse les URLs manuelles
        generator = RedirectGenerator()
        final_new_urls = generator.parse_urls(new_urls_manual)
        new_source = "manuel"
    else:
        new_source = "aucun"
    
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

    # Instructions d'utilisation
    with st.expander("📋 Instructions & aide"):
        st.markdown("""
        ### 🔄 Mode hybride (recommandé)
        **Pour chaque site, choisissez votre méthode :**
        
        #### 🤖 Scraping automatique
        1. **Entrez l'URL** (ex: https://ancien-site.com)
        2. **Cliquez "Scraper"** - L'outil explore automatiquement jusqu'à 200 pages
        3. **Vérifiez le résultat** (succès ou échec)
        
        #### ✏️ Saisie manuelle 
        1. **Collez vos URLs** dans le champ texte
        2. **Formats supportés** : sitemap XML, liste brute, CSV
        
        ### 💡 Flexibilité totale
        - **Scraper l'ancien + Manuel nouveau** : Si robots.txt bloque le nouveau site
        - **Manuel ancien + Scraper nouveau** : Si l'ancien site est inaccessible
        - **Tout scraping** : Si les deux sites sont accessibles
        - **Tout manuel** : Pour un contrôle total
        
        ### 📤 Formats supportés (saisie manuelle)
        - **Sitemap XML** : Balises `<loc>...</loc>`
        - **Liste brute** : Une URL par ligne
        - **CSV** : Deux colonnes
        
        ### ⚠️ Dépannage
        - **Scraping échoue** → Passez en manuel pour ce site
        - **Robots.txt bloque** → Utilisez la saisie manuelle
        - **Site avec auth** → Exportez manuellement le sitemap
        - **Nombre d'URLs différent** → Pas de problème, génération adaptative
        """)
    
    # Footer
    st.markdown("---")
    st.markdown("*Développé pour SEPTEO Digital Services — Fire Salamander Team* 🦎")
    st.markdown("*v2.1 avec mode hybride flexible (scraping + manuel)*")

if __name__ == "__main__":
    main()