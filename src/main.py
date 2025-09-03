"""
Interface Streamlit pour le générateur de redirections 301
"""

import streamlit as st
import csv
import io
from generator import RedirectGenerator

# Configuration de la page
st.set_page_config(
    page_title="301 Redirect Generator",
    page_icon="🦎",
    layout="wide"
)

def main():
    """Interface principale"""
    
    # Titre
    st.title("🦎 301 Redirect Generator")
    st.markdown("Générez vos redirections 301 en un clic")
    st.markdown("---")
    
    # Instructions
    with st.expander("📋 Instructions d'utilisation"):
        st.markdown("""
        1. **Collez vos anciennes URLs** dans le premier champ
        2. **Collez vos nouvelles URLs** dans le second champ
        3. **Cliquez sur Générer** les redirections
        4. **Téléchargez** vos fichiers .htaccess et .csv
        
        **Formats supportés :**
        - Sitemap XML (balises `<loc>`)
        - Liste brute (une URL par ligne)
        - CSV copié (deux colonnes)
        """)
    
    # Interface principale
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔗 Anciennes URLs")
        old_urls_input = st.text_area(
            label="Anciennes URLs",
            placeholder="Collez ici vos anciennes URLs...\nExemple:\nhttps://ancien-site.com/page1\nhttps://ancien-site.com/page2",
            height=300,
            label_visibility="collapsed"
        )
    
    with col2:
        st.subheader("🎯 Nouvelles URLs") 
        new_urls_input = st.text_area(
            label="Nouvelles URLs",
            placeholder="Collez ici vos nouvelles URLs...\nExemple:\nhttps://nouveau-site.com/nouvelle-page1\nhttps://nouveau-site.com/nouvelle-page2",
            height=300,
            label_visibility="collapsed"
        )
    
    # Bouton de génération
    st.markdown("---")
    
    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
    with col_btn2:
        generate_button = st.button("🚀 Générer les redirections", use_container_width=True, type="primary")
    
    # Traitement
    if generate_button:
        if not old_urls_input.strip() or not new_urls_input.strip():
            st.error("❌ Veuillez remplir les deux champs avant de générer les redirections.")
            return
        
        try:
            # Génération
            generator = RedirectGenerator()
            htaccess_content, csv_data = generator.generate_redirections(old_urls_input, new_urls_input)
            
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
            
        except ValueError as e:
            st.error(f"❌ Erreur de correspondance: {str(e)}")
            st.info("💡 Vérifiez que vous avez le même nombre d'URLs dans les deux listes.")
        except Exception as e:
            st.error(f"❌ Erreur lors de la génération: {str(e)}")
    
    # Footer
    st.markdown("---")
    st.markdown("*Développé pour SEPTEO Digital Services — Fire Salamander Team* 🦎")

if __name__ == "__main__":
    main()