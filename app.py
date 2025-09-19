"""
Fire Snake 301 - Application principale
Point d'entrée pour l'interface Streamlit
"""

import os
import sys
from dotenv import load_dotenv

# Charge les variables d'environnement dès le début
load_dotenv()

# Ajoute le répertoire src au path Python
sys.path.append('src')

import streamlit as st
from src.advanced_interface import interface_ai_avancee, interface_classique
from src.config import APP_VERSION, APP_NAME, APP_DESCRIPTION

def main():
    """Point d'entrée principal de l'application"""
    
    # Configuration de la page Streamlit
    st.set_page_config(
        page_title=f"{APP_NAME} v{APP_VERSION}",
        page_icon="🐍",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Header principal
    st.title(f"🐍 {APP_NAME}")
    st.caption(f"v{APP_VERSION} - {APP_DESCRIPTION}")
    
    # Sidebar pour choisir l'interface
    with st.sidebar:
        st.header("🔧 Mode d'utilisation")
        
        interface_mode = st.radio(
            "Choisissez votre interface :",
            ["🤖 Interface IA avancée", "🔄 Interface classique"],
            index=0,
            help="Interface IA : matching sémantique intelligent\nInterface classique : mapping alphabétique"
        )
        
        st.divider()
        
        # Informations système
        st.subheader("📊 Informations")
        st.text(f"Version: {APP_VERSION}")
        
        # Vérification clé OpenAI
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            st.success("✅ Clé OpenAI configurée")
        else:
            st.error("❌ Clé OpenAI manquante")
            st.info("Configurez OPENAI_API_KEY dans le fichier .env")
    
    # Affichage de l'interface sélectionnée
    if "🤖 Interface IA avancée" in interface_mode:
        interface_ai_avancee()
    else:
        interface_classique()
    
    # Footer
    st.divider()
    st.caption("🔥 Fire Snake 301 - Générateur de redirections intelligent")

if __name__ == "__main__":
    main()