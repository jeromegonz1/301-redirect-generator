"""
Interface avancée avec IA sémantique et support multilangue
"""

import os
from dotenv import load_dotenv

# Charge les variables d'environnement
load_dotenv()

import streamlit as st
import csv
import io
from typing import List, Dict, Any
from urllib.parse import urlparse
from generator import RedirectGenerator
from scraper import crawl_site_with_fallback, WebScraper, parse_sitemap
from src.smart_input_parser import SmartInputParser
from language_detector import LanguageDetector
from ai_mapper import AIMapper, AIMatchingError
from fallback_manager import FallbackManager
from domain_detector import DomainDetector
from cache_manager import CacheManager
from fallback_302_intelligent import Fallback302Intelligent
from config import APP_VERSION, APP_NAME, APP_DESCRIPTION, APP_METADATA

# Import pour export XLS Balt (Sprint 3.5)
try:
    import openpyxl
    from openpyxl import Workbook
    OPENPYXL_AVAILABLE = True
except ImportError:
    OPENPYXL_AVAILABLE = False


def url_to_relative_path(url: str) -> str:
    """
    Convertit une URL absolue en chemin relatif pour .htaccess
    
    Args:
        url: URL absolue (ex: http://site.com/path/page)
        
    Returns:
        Chemin relatif (ex: /path/page)
    """
    if not url or not isinstance(url, str):
        return "/"
    
    parsed = urlparse(url.strip())
    path = parsed.path if parsed.path else "/"
    
    # Assure qu'on a un slash au début
    if not path.startswith('/'):
        path = '/' + path
    
    return path


def convert_url_domain(old_url: str, target_domain: str) -> str:
    """
    Convertit une URL d'un domaine vers un autre en conservant le path
    
    Args:
        old_url: URL source (ex: https://www.campinglescascades.com/fr/page)
        target_domain: Domaine cible (ex: https://www.les-cascades.com)
        
    Returns:
        URL avec nouveau domaine (ex: https://www.les-cascades.com/fr/page)
    """
    if not old_url or not isinstance(old_url, str):
        return target_domain
    
    parsed = urlparse(old_url.strip())
    path = parsed.path if parsed.path else "/"
    query = f"?{parsed.query}" if parsed.query else ""
    fragment = f"#{parsed.fragment}" if parsed.fragment else ""
    
    # S'assurer que le domaine cible se termine sans slash
    target_domain = target_domain.rstrip('/')
    
    return f"{target_domain}{path}{query}{fragment}"


def extract_language_from_url_path(url: str) -> str:
    """
    Extrait la langue depuis une URL en analysant le path
    
    Args:
        url: URL à analyser
        
    Returns:
        Code langue (fr, en, de, nl, etc.) ou 'fr' par défaut
    """
    if not url:
        return "fr"
    
    path = url_to_relative_path(url)
    
    # Patterns de langue supportés : /fr/, /en/, /de/, /nl/, /es/, /it/
    languages = ['fr', 'en', 'de', 'nl', 'es', 'it']
    
    for lang in languages:
        if f"/{lang}/" in path or path.startswith(f"/{lang}"):
            return lang
    
    return "fr"  # Fallback par défaut


def remove_duplicate_redirects(redirects: List[Dict]) -> List[Dict]:
    """
    Filtre les redirections pour éviter les doublons et privilégier l'IA vs fallback
    
    Philosophy Fire Snake 301: 
    - Fallback 302 UNIQUEMENT pour URLs non matchées par IA
    - Priorité aux correspondances IA (confidence > 0) sur fallbacks (confidence = 0)
    
    Args:
        redirects: Liste des redirections avec 'source', 'target', 'confidence'
        
    Returns:
        Liste filtrée sans doublons, IA prioritaire sur fallback
    """
    source_map = {}  # source -> best redirect
    
    for redirect in redirects:
        source = redirect.get('source', '')
        target = redirect.get('target', '')
        confidence = redirect.get('confidence', 0.0)
        
        # Ignorer si source == target  
        if source == target:
            continue
        
        # Si source déjà vue, compare les confidences
        if source in source_map:
            existing_redirect = source_map[source]
            existing_confidence = existing_redirect.get('confidence', 0.0)
            
            # Privilégie la redirection avec la plus haute confidence
            # IA (confidence > 0) l'emporte toujours sur fallback (confidence = 0)
            if confidence > existing_confidence:
                source_map[source] = redirect
        else:
            source_map[source] = redirect
    
    return list(source_map.values())


def generate_balt_xlsx(redirects_data: List[Dict], output_path: str = None, output_dir: str = None) -> str:
    """
    Génère un fichier Excel (.xlsx) au format Balt pour import automatique Septeo
    
    Format Balt:
    - 2 colonnes exactement: Source, Target
    - URLs absolues uniquement (source ET target)
    - Pas de commentaires, confidence ou type redirection
    - UTF-8, nom: redirections_balt.xlsx
    
    Args:
        redirects_data: Liste des redirections avec 'source' et 'target'
        output_path: Chemin complet du fichier de sortie (optionnel)
        output_dir: Répertoire de sortie (si output_path non spécifié)
        
    Returns:
        Chemin du fichier Excel généré
        
    Raises:
        ImportError: Si openpyxl n'est pas disponible
        ValueError: Si les données sont invalides
    """
    if not OPENPYXL_AVAILABLE:
        raise ImportError("openpyxl requis pour l'export XLS. Installation: pip install openpyxl")
    
    # Détermination du chemin de sortie
    if not output_path:
        if output_dir:
            output_path = os.path.join(output_dir, 'redirections_balt.xlsx')
        else:
            output_path = 'redirections_balt.xlsx'
    
    # Création du workbook Excel
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = "Redirections"
    
    # En-têtes (ligne 1) - Format Balt exact
    worksheet['A1'] = 'Source'
    worksheet['B1'] = 'Target'
    
    # Données (à partir de la ligne 2)
    current_row = 2
    for redirect in redirects_data:
        source = redirect.get('source', '')
        target = redirect.get('target', '')
        
        # Debug: Log des données reçues
        print(f"[DEBUG EXCEL] Source: '{source}' | Target: '{target}'")
        
        # Validation: URLs absolues uniquement pour format Balt
        if source.startswith('https://') or source.startswith('http://'):
            if target.startswith('https://') or target.startswith('http://'):
                worksheet[f'A{current_row}'] = source
                worksheet[f'B{current_row}'] = target
                current_row += 1
            else:
                print(f"[DEBUG EXCEL] Target invalide (pas absolu): '{target}'")
        else:
            print(f"[DEBUG EXCEL] Source invalide (pas absolu): '{source}'")
    
    # Sauvegarde du fichier Excel
    try:
        workbook.save(output_path)
        workbook.close()
        
        # Vérification que le fichier a été créé
        if not os.path.exists(output_path):
            raise FileNotFoundError(f"Échec création fichier: {output_path}")
            
        return output_path
        
    except Exception as e:
        # Nettoyage en cas d'erreur
        if 'workbook' in locals():
            workbook.close()
        if os.path.exists(output_path):
            try:
                os.remove(output_path)
            except:
                pass
        raise ValueError(f"Erreur génération XLS Balt: {str(e)}")


def interface_ai_avancee():
    """Interface avancée avec IA sémantique et multilangue"""
    
    st.header("🚀 Générateur IA avec support multilangue")
    st.info("ℹ️ Cette interface utilise GPT-3.5-turbo pour le matching sémantique intelligent des URLs")
    
    # Initialisation du gestionnaire de cache
    cache_manager = CacheManager()
    
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
    
    # Configuration Fallback 302 Intelligent (Sprint 3)
    with st.expander("🔄 Fallback intelligent 302 (Sprint 3)"):
        enable_fallback_302 = st.checkbox(
            "✅ Activer fallback 302 automatique", 
            value=True,
            help="Redirige automatiquement les URLs non matchées vers la page d'accueil de leur langue (302 temporaire)"
        )
        
        if enable_fallback_302:
            st.info("🎯 Les URLs sans correspondance IA seront redirigées en 302 vers /langue/")
            st.write("**Exemple :** `/fr/page-orpheline` → `Redirect 302 /fr/page-orpheline /fr/`")
        else:
            st.warning("⚠️ URLs non matchées ignoreront les fallback (peut générer des 404)")
    
    # Gestion du cache
    with st.expander("💾 Gestion du cache (évite les appels API répétés)"):
        col_cache1, col_cache2 = st.columns(2)
        
        with col_cache1:
            # Statistiques du cache
            cache_stats = cache_manager.get_cache_stats()
            st.metric("Résultats en cache", cache_stats["gpt_cache_files"])
            st.metric("Fichiers .htaccess", cache_stats["htaccess_files"])
            
        with col_cache2:
            st.metric("Taille cache", f"{cache_stats['total_size_mb']} MB")
            if st.button("🧹 Nettoyer cache (>7j)"):
                deleted = cache_manager.clear_old_cache()
                st.success(f"✅ {deleted} fichiers supprimés")
        
        # Affichage des caches récents
        cached_results = cache_manager.list_cached_results()
        if cached_results:
            st.write("**Résultats récents en cache:**")
            for i, cache_info in enumerate(cached_results[:3]):  # Affiche les 3 plus récents
                st.text(f"• {cache_info['timestamp'][:16]} - {cache_info['old_urls_count']} → {cache_info['new_urls_count']} URLs")
    
    # Collecte des URLs
    st.header("📊 Collecte des URLs")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔗 Ancien site")
        old_input_mode = st.radio("Mode", ["URL à scraper", "Sitemap XML", "Input universel", "Liste manuelle"], key="old")
        
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
        elif old_input_mode == "Sitemap XML":
            old_sitemap_url = st.text_input("URL du sitemap ancien site", placeholder="https://ancien-site.com/sitemap.xml")
            if st.button("🗺️ Parser sitemap ancien site"):
                if old_sitemap_url:
                    with st.spinner("Parsing du sitemap..."):
                        old_urls = parse_sitemap(old_sitemap_url)
                        st.session_state.old_urls = old_urls
                        st.success(f"✅ {len(old_urls)} URLs extraites du sitemap")
                else:
                    st.error("Veuillez entrer une URL de sitemap")
        elif old_input_mode == "Input universel":
            st.info("🎯 Collez n'importe quel format: XML, JSON, CSV ou liste d'URLs")
            old_universal_input = st.text_area("Input universel (auto-détection)", height=200, key="old_universal", 
                                             placeholder="Collez ici votre sitemap XML, JSON, CSV ou liste d'URLs...")
            if st.button("🧠 Parser avec IA (auto-détection)"):
                if old_universal_input:
                    with st.spinner("Auto-détection et parsing en cours..."):
                        try:
                            parser = SmartInputParser()
                            old_urls = parser.detect_and_parse(old_universal_input)
                            st.session_state.old_urls = old_urls
                            
                            # Affiche le format détecté
                            detected_format = parser.detect_format(old_universal_input)
                            st.success(f"✅ Format détecté: {detected_format.upper()} | {len(old_urls)} URLs extraites")
                        except Exception as e:
                            st.error(f"❌ Erreur parsing: {str(e)}")
                else:
                    st.error("Veuillez coller votre input")
        else:
            old_text = st.text_area("URLs (une par ligne)", height=200, key="old_manual")
            if old_text:
                st.session_state.old_urls = [url.strip() for url in old_text.split('\n') if url.strip()]
    
    with col2:
        st.subheader("🎯 Nouveau site")
        new_input_mode = st.radio("Mode", ["Sitemap XML", "Input universel", "Liste manuelle"], key="new")
        
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
        elif new_input_mode == "Input universel":
            st.info("🎯 Collez n'importe quel format: XML, JSON, CSV ou liste d'URLs")
            new_universal_input = st.text_area("Input universel (auto-détection)", height=200, key="new_universal",
                                             placeholder="Collez ici votre sitemap XML, JSON, CSV ou liste d'URLs...")
            if st.button("🧠 Parser nouveau site (auto-détection)"):
                if new_universal_input:
                    with st.spinner("Auto-détection et parsing en cours..."):
                        try:
                            parser = SmartInputParser()
                            new_urls = parser.detect_and_parse(new_universal_input)
                            st.session_state.new_urls = new_urls
                            
                            # Affiche le format détecté
                            detected_format = parser.detect_format(new_universal_input)
                            st.success(f"✅ Format détecté: {detected_format.upper()} | {len(new_urls)} URLs extraites")
                        except Exception as e:
                            st.error(f"❌ Erreur parsing: {str(e)}")
                else:
                    st.error("Veuillez coller votre input")
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
        
        # Configuration domaine cible
        st.header("🌐 Configuration domaine cible")
        
        # Détection intelligente du domaine cible
        domain_detector = DomainDetector()
        
        # Utilise la session state pour persister la suggestion
        if 'suggested_domain' not in st.session_state:
            st.session_state.suggested_domain = ""
        
        # Recalcule la suggestion si les URLs de l'ancien site changent
        current_old_urls = getattr(st.session_state, 'old_urls', [])
        # S'assurer que current_old_urls contient des strings, pas des listes
        if current_old_urls and isinstance(current_old_urls[0], list):
            # Aplatir si c'est une liste de listes
            current_old_urls = [url for sublist in current_old_urls for url in sublist if isinstance(url, str)]
        elif current_old_urls:
            # S'assurer que tous les éléments sont des strings
            current_old_urls = [str(url) for url in current_old_urls if url]
        current_old_urls_str = '\n'.join(current_old_urls) if current_old_urls else ""
        
        if current_old_urls_str != st.session_state.get('last_old_urls_str', ''):
            st.session_state.last_old_urls_str = current_old_urls_str
            if current_old_urls:
                st.session_state.suggested_domain = domain_detector.suggest_target_domain(
                    current_old_urls_str, 
                    st.session_state.get('target_domain_value', '')
                )
        
        # Input avec suggestion intelligente
        suggested_domain = st.session_state.suggested_domain or ""
        
        target_domain = st.text_input(
            "Domaine cible pour les redirections",
            placeholder="https://www.example.com",
            help="🧠 Auto-détecté depuis l'ancien site. Modifiez si nécessaire.",
            value=suggested_domain,
            key="target_domain_input"
        )
        
        # Sauvegarde la valeur pour la prochaine suggestion
        st.session_state.target_domain_value = target_domain
        
        if not target_domain:
            st.error("⚠️ Domaine cible requis pour générer les redirections absolues")
            return
        
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
            with st.spinner("🧠 Vérification du cache..."):
                try:
                    # Vérification du cache d'abord
                    cache_key_info = f"Temp:{temperature}, Chunk:{chunk_size}, Seuil:{confidence_threshold}"
                    cached_result = cache_manager.get_gpt_cache(
                        old_urls, new_urls, contexte_metier, temperature
                    )
                    
                    if cached_result:
                        st.success(f"✅ Résultats trouvés en cache ! (Économie API)")
                        # Utilise les résultats du cache
                        all_matches = cached_result["results"]["all_matches"]
                        all_unmatched = cached_result["results"]["all_unmatched"]
                        missing_langs = cached_result["results"]["missing_langs"]
                        old_grouped = cached_result["results"]["old_grouped"]
                        
                        st.info(f"📊 Cache utilisé: {len(all_matches)} correspondances trouvées")
                    else:
                        st.info("💸 Appel API GPT nécessaire - Nouveau matching...")
                        
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
                        
                        # Sauvegarde des résultats dans le cache
                        gpt_results = {
                            "all_matches": all_matches,
                            "all_unmatched": all_unmatched,
                            "missing_langs": missing_langs,
                            "old_grouped": old_grouped
                        }
                        
                        cache_file = cache_manager.save_gpt_cache(
                            old_urls, new_urls, contexte_metier, temperature, gpt_results
                        )
                        st.success(f"💾 Résultats sauvegardés en cache: {cache_file}")
                    
                    # Les variables all_matches, all_unmatched, etc. sont maintenant disponibles
                    # que ce soit depuis le cache ou depuis l'API GPT
                    
                    # Sprint 3 - Traitement intelligent des URLs non matchées
                    fallback_302_results = {}
                    fallback_302_csv_data = []
                    
                    if enable_fallback_302 and all_unmatched:
                        st.subheader("🔄 Fallback intelligent 302 (Sprint 3)")
                        
                        # Initialisation du gestionnaire fallback 302
                        intelligent_fallback = Fallback302Intelligent(
                            enable_fallback_302=True,
                            default_fallback_lang=fallback_lang
                        )
                        
                        # Traitement des URLs non matchées
                        ai_session_results = {
                            "matched_urls": all_matches,
                            "unmatched_urls": all_unmatched
                        }
                        
                        fallback_302_results = intelligent_fallback.process_ai_results(ai_session_results)
                        
                        # Affichage des résultats fallback
                        nb_fallback = len(fallback_302_results["fallback_302_redirects"])
                        if nb_fallback > 0:
                            st.success(f"✅ {nb_fallback} redirections 302 fallback générées")
                            
                            # Préparation des données CSV pour export
                            fallback_302_csv_data = fallback_302_results["csv_export_data"]
                            
                            # Affichage d'un échantillon
                            with st.expander(f"🔍 Aperçu des {min(3, nb_fallback)} premières redirections 302"):
                                for redirect in fallback_302_results["fallback_302_redirects"][:3]:
                                    st.code(f"Redirect 302 {redirect['old_url']} {redirect['target_url']}")
                        else:
                            st.info("ℹ️ Aucune URL non matchée nécessitant de fallback 302")
                    elif not enable_fallback_302 and all_unmatched:
                        st.warning(f"⚠️ {len(all_unmatched)} URLs non matchées (fallback 302 désactivé)")
                    
                    # Fin Sprint 3 - Fallback intelligent
                    
                    # Génération des redirections 302 pour langues manquantes
                    redirects_302 = []
                    if missing_langs:
                        redirects_302 = fallback_manager.generate_302_redirects(
                            missing_langs, old_grouped, fallback_lang
                        )
                    
                    # Génération du fichier .htaccess final avec URLs absolues
                    st.subheader("📄 Fichier .htaccess avec URLs absolues")
                    
                    # Préparation de toutes les redirections avec URLs absolues
                    all_redirects = []
                    
                    # 1. Ajout des matches IA avec commentaires (301)
                    for match in all_matches:
                        source = match['ancienne']
                        target = match['nouvelle']
                        
                        # Conversion target vers domaine cible (URLs absolues)
                        target_absolute = convert_url_domain(target, target_domain)
                        confidence = match.get('confidence', 0)
                        reason = match.get('raison', '')
                        
                        all_redirects.append({
                            'type': '301',
                            'source': source,
                            'target': target_absolute,
                            'comment': f"# {reason} (confiance: {confidence:.2f})",
                            'confidence': confidence
                        })
                    
                    # 2. Ajout des fallback 302 intelligents avec URLs absolues
                    if enable_fallback_302 and all_unmatched:
                        for unmatched_url in all_unmatched:
                            language = extract_language_from_url_path(unmatched_url)
                            
                            # Logique française : langue principale à la racine, autres langues avec préfixe
                            if language == fallback_lang:
                                target_fallback = f"{target_domain}/"  # Langue principale à la racine
                            else:
                                target_fallback = f"{target_domain}/{language}/"  # Autres langues avec préfixe
                            
                            all_redirects.append({
                                'type': '302',
                                'source': unmatched_url,
                                'target': target_fallback,
                                'comment': f"# Fallback 302 vers la home {language.upper()}",
                                'confidence': 0
                            })
                    
                    # 3. Ajout des redirections 302 pour langues manquantes  
                    if missing_langs:
                        redirects_302 = fallback_manager.generate_302_redirects(
                            missing_langs, old_grouped, fallback_lang
                        )
                        for source, target_relative in redirects_302:
                            target_absolute = f"{target_domain}{target_relative}"
                            language = extract_language_from_url_path(source)
                            
                            all_redirects.append({
                                'type': '302',
                                'source': source,
                                'target': target_absolute,
                                'comment': f"# Langue {language.upper()} non migrée",
                                'confidence': 0
                            })
                    
                    # 4. Filtrage des doublons et source == cible
                    filtered_redirects = remove_duplicate_redirects(all_redirects)
                    
                    # 5. Construction du .htaccess final
                    htaccess_lines = [
                        "# Redirections 301/302 avec URLs absolues",
                        "# Fire Snake 301 - Sprint 3 Enhanced",
                        "# Format: Source absolue → Target absolue",
                        ""
                    ]
                    
                    # Séparation 301 et 302 pour meilleure organisation
                    redirects_301 = [r for r in filtered_redirects if r['type'] == '301']
                    redirects_302 = [r for r in filtered_redirects if r['type'] == '302']
                    
                    # Ajout des 301 avec commentaires IA
                    if redirects_301:
                        htaccess_lines.extend([
                            "# ===================================================",
                            "# REDIRECTIONS 301 - MATCHING IA SÉMANTIQUE",
                            "# ===================================================",
                            ""
                        ])
                        
                        for redirect in redirects_301:
                            htaccess_lines.append(redirect['comment'])
                            htaccess_lines.append(f"Redirect 301 {redirect['source']} {redirect['target']}")
                            htaccess_lines.append("")
                    
                    # Ajout des 302 avec commentaires simplifiés
                    if redirects_302:
                        htaccess_lines.extend([
                            "# ===================================================",
                            "# REDIRECTIONS 302 - FALLBACK INTELLIGENT",
                            "# URLs orphelines → Page d'accueil langue",
                            "# ===================================================",
                            ""
                        ])
                        
                        for redirect in redirects_302:
                            htaccess_lines.append(redirect['comment'])
                            htaccess_lines.append(f"Redirect 302 {redirect['source']} {redirect['target']}")
                            htaccess_lines.append("")
                    
                    # 6. Génération du contenu final .htaccess
                    htaccess_content = "\n".join(htaccess_lines)
                    
                    # 7. Résumé statistiques en console (BONUS)
                    st.subheader("📊 Résumé de génération")
                    
                    total_301 = len(redirects_301)
                    total_302 = len(redirects_302)
                    total_redirects = total_301 + total_302
                    total_old_urls = len(old_urls)
                    
                    # Calcul du taux de correspondance IA
                    if total_old_urls > 0:
                        taux_correspondance = (total_301 / total_old_urls) * 100
                    else:
                        taux_correspondance = 0
                    
                    # Affichage des métriques
                    col_stats1, col_stats2, col_stats3, col_stats4 = st.columns(4)
                    
                    with col_stats1:
                        st.metric("✅ Redirections 301", total_301, help="Correspondances IA trouvées")
                    
                    with col_stats2:
                        st.metric("↪️ Redirections 302", total_302, help="Fallback automatiques")
                    
                    with col_stats3:
                        st.metric("🎯 Taux correspondance", f"{taux_correspondance:.1f}%", help="% URLs matchées par IA")
                    
                    with col_stats4:
                        st.metric("🔧 Total redirections", total_redirects, help="301 + 302 combinées")
                    
                    # Message récapitulatif style console
                    st.code(f"""✅ {total_301} redirections 301 générées
↪️ {total_302} redirections 302 fallback  
🎯 Taux de correspondance IA : {taux_correspondance:.2f}%
📄 Fichier .htaccess prêt pour production avec URLs absolues""", language="text")
                    
                    # Sauvegarde automatique du fichier .htaccess
                    htaccess_file_path = cache_manager.save_htaccess_file(
                        htaccess_content, old_urls, new_urls, "ai_semantic"
                    )
                    st.success(f"💾 Fichier .htaccess sauvegardé: {htaccess_file_path}")
                    
                    # Affichage et téléchargement
                    st.code(htaccess_content, language="apache")
                    
                    # Sprint 3.5 - Ajout de la colonne pour export XLS Balt
                    if OPENPYXL_AVAILABLE:
                        if enable_fallback_302 and fallback_302_csv_data:
                            col_dl1, col_dl2, col_dl3, col_dl4, col_dl5 = st.columns(5)
                        else:
                            col_dl1, col_dl2, col_dl3, col_dl4 = st.columns(4)
                    else:
                        # Fallback si openpyxl non disponible
                        if enable_fallback_302 and fallback_302_csv_data:
                            col_dl1, col_dl2, col_dl3, col_dl4 = st.columns(4)
                        else:
                            col_dl1, col_dl2, col_dl3 = st.columns(3)
                    
                    with col_dl1:
                        st.download_button(
                            label="⬇️ Télécharger .htaccess",
                            data=htaccess_content,
                            file_name="htaccess_ai_semantic.txt",
                            mime="text/plain"
                        )
                    
                    with col_dl2:
                        # Génération du CSV détaillé avec URLs absolues
                        csv_data = [["Source", "Target", "Type", "Confidence", "Reason", "Language"]]
                        
                        # Utilisation des redirections filtrées pour le CSV
                        for redirect in filtered_redirects:
                            csv_data.append([
                                redirect['source'],
                                redirect['target'],  # URLs absolues maintenant
                                redirect['type'],
                                f"{redirect.get('confidence', 0):.2f}",
                                redirect['comment'].replace('# ', ''),  # Nettoyage du commentaire
                                extract_language_from_url_path(redirect['source'])
                            ])
                        
                        csv_buffer = io.StringIO()
                        csv_writer = csv.writer(csv_buffer)
                        csv_writer.writerows(csv_data)
                        
                        st.download_button(
                            label="⬇️ CSV Complet",
                            data=csv_buffer.getvalue(),
                            file_name="redirections_absolues_301_302.csv",
                            mime="text/csv",
                            help="CSV avec toutes les redirections (URLs absolues)"
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
                    
                    # Sprint 3 - Bouton export CSV fallback 302
                    if enable_fallback_302 and fallback_302_csv_data:
                        with col_dl4:
                            # Export CSV des fallback 302
                            intelligent_fallback = Fallback302Intelligent()
                            fallback_csv_content = intelligent_fallback.export_to_csv(fallback_302_csv_data)
                            
                            st.download_button(
                                label="🔄 CSV Fallback 302",
                                data=fallback_csv_content,
                                file_name="fallback_302_urls.csv",
                                mime="text/csv",
                                help="URLs non matchées avec redirections 302 temporaires"
                            )
                    
                    # Sprint 3.5 - Export XLS Balt (nouveau bouton)
                    if OPENPYXL_AVAILABLE:
                        if enable_fallback_302 and fallback_302_csv_data:
                            col_xls = col_dl5  # 5ème colonne si fallback 302 activé
                        else:
                            col_xls = col_dl4  # 4ème colonne sinon
                            
                        with col_xls:
                            # Génération du fichier XLS Balt en mémoire
                            try:
                                import tempfile
                                with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp_file:
                                    balt_file_path = generate_balt_xlsx(filtered_redirects, tmp_file.name)
                                    
                                    # Lecture du fichier pour téléchargement
                                    with open(balt_file_path, 'rb') as f:
                                        balt_data = f.read()
                                    
                                    # Nettoyage du fichier temporaire
                                    try:
                                        os.unlink(balt_file_path)
                                    except:
                                        pass
                                    
                                    st.download_button(
                                        label="💾 Export XLS (Balt)",
                                        data=balt_data,
                                        file_name="redirections_balt.xlsx",
                                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                        help="Format XLS compatible Septeo BALT CMS (2 colonnes Source/Target uniquement)"
                                    )
                            except Exception as e:
                                st.error(f"❌ Erreur export XLS: {str(e)}")
                                st.info("💡 Vérifiez que openpyxl est installé: `pip install openpyxl`")
                
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