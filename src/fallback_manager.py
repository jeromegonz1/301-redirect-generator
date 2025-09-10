"""
Gestionnaire de fallbacks 302 pour langues non migrées (US013)
Aucun hardcoding - Configuration flexible
"""

from typing import List, Tuple, Dict, Set
try:
    from language_detector import LanguageDetector
except ImportError:
    from src.language_detector import LanguageDetector


class FallbackManager:
    """Gestionnaire des redirections 302 pour langues manquantes"""
    
    def __init__(self, default_fallback_lang: str = "fr"):
        """
        Initialise le gestionnaire de fallbacks
        
        Args:
            default_fallback_lang: Langue cible pour les redirections 302
        """
        self.default_fallback_lang = default_fallback_lang
        self.detector = LanguageDetector()
    
    def detect_missing_languages(self, old_urls: List[str], new_urls: List[str]) -> List[str]:
        """
        Détecte les langues présentes dans ancien site mais absentes du nouveau
        
        Args:
            old_urls: URLs de l'ancien site
            new_urls: URLs du nouveau site
            
        Returns:
            Liste des langues manquantes
        """
        old_grouped = self.detector.group_by_language(old_urls)
        new_grouped = self.detector.group_by_language(new_urls)
        
        old_languages = set(old_grouped.keys())
        new_languages = set(new_grouped.keys())
        
        missing = old_languages - new_languages
        return sorted(list(missing))
    
    def generate_302_redirects(self, missing_langs: List[str], 
                              old_urls_grouped: Dict[str, List[str]], 
                              fallback_lang: str = None) -> List[Tuple[str, str]]:
        """
        Génère les redirections 302 pour langues manquantes
        
        Args:
            missing_langs: Langues à rediriger
            old_urls_grouped: URLs groupées par langue
            fallback_lang: Langue cible (défaut: self.default_fallback_lang)
            
        Returns:
            Liste de tuples (url_source, url_cible)
        """
        if fallback_lang is None:
            fallback_lang = self.default_fallback_lang
        
        redirects = []
        fallback_target = f"/{fallback_lang}/"
        
        for lang in missing_langs:
            if lang in old_urls_grouped:
                for url in old_urls_grouped[lang]:
                    redirects.append((url, fallback_target))
        
        return redirects
    
    def format_htaccess_302(self, redirects: List[Tuple[str, str]]) -> str:
        """
        Formate les redirections 302 en syntaxe Apache
        
        Args:
            redirects: Liste de tuples (source, cible)
            
        Returns:
            Contenu .htaccess formaté
        """
        if not redirects:
            return ""
        
        lines = [
            "# Redirections temporaires pour langues non migrées",
            "# Générées automatiquement par Fire Snake 301",
            ""
        ]
        
        # Grouper par langue cible pour organisation
        grouped_by_target = {}
        for source, target in redirects:
            if target not in grouped_by_target:
                grouped_by_target[target] = []
            grouped_by_target[target].append(source)
        
        # Générer les redirections groupées
        for target, sources in grouped_by_target.items():
            # Déterminer la langue source depuis la première URL
            if sources:
                source_lang = self.detector.detect(sources[0])
                lang_comment = self._get_language_comment(source_lang, target)
                lines.append(f"# {lang_comment}")
                
                for source in sources:
                    lines.append(f"Redirect 302 {source} {target}")
                
                lines.append("")  # Ligne vide entre les groupes
        
        return "\n".join(lines)
    
    def _get_language_comment(self, source_lang: str, target: str) -> str:
        """Génère un commentaire explicatif pour une redirection de langue"""
        lang_names = {
            'fr': 'Français',
            'en': 'Anglais', 
            'de': 'Allemand',
            'es': 'Espagnol',
            'it': 'Italien',
            'nl': 'Néerlandais'
        }
        
        source_name = lang_names.get(source_lang, source_lang.upper())
        target_lang = target.strip('/').lower()
        target_name = lang_names.get(target_lang, target_lang.upper())
        
        return f"{source_name} → {target_name} (temporaire)"
    
    def get_fallback_stats(self, old_urls: List[str], new_urls: List[str]) -> Dict[str, any]:
        """
        Génère des statistiques sur les fallbacks nécessaires
        
        Returns:
            Statistiques détaillées
        """
        old_grouped = self.detector.group_by_language(old_urls)
        new_grouped = self.detector.group_by_language(new_urls)
        missing_langs = self.detect_missing_languages(old_urls, new_urls)
        
        stats = {
            "total_old_urls": len(old_urls),
            "total_new_urls": len(new_urls),
            "languages_old": len(old_grouped),
            "languages_new": len(new_grouped),
            "missing_languages": missing_langs,
            "fallback_count": 0,
            "language_details": {}
        }
        
        # Détails par langue
        for lang in old_grouped.keys():
            old_count = len(old_grouped[lang])
            new_count = len(new_grouped.get(lang, []))
            is_missing = lang in missing_langs
            
            stats["language_details"][lang] = {
                "old_count": old_count,
                "new_count": new_count,
                "missing": is_missing,
                "fallback_needed": old_count if is_missing else 0
            }
            
            if is_missing:
                stats["fallback_count"] += old_count
        
        stats["fallback_percentage"] = round(
            (stats["fallback_count"] / stats["total_old_urls"]) * 100, 1
        ) if stats["total_old_urls"] > 0 else 0
        
        return stats
    
    def generate_fallback_report(self, old_urls: List[str], new_urls: List[str]) -> str:
        """
        Génère un rapport textuel des fallbacks nécessaires
        
        Returns:
            Rapport formaté en texte
        """
        stats = self.get_fallback_stats(old_urls, new_urls)
        
        lines = [
            "📈 Rapport des redirections temporaires",
            "",
            f"📊 Vue d'ensemble :",
            f"├── Total URLs ancien site : {stats['total_old_urls']}",
            f"├── Total URLs nouveau site : {stats['total_new_urls']}",
            f"├── Langues ancien site : {stats['languages_old']}",
            f"├── Langues nouveau site : {stats['languages_new']}",
            f"└── URLs nécessitant fallback : {stats['fallback_count']} ({stats['fallback_percentage']}%)",
            ""
        ]
        
        if stats["missing_languages"]:
            lines.append("🚨 Langues non migrées :")
            for lang in stats["missing_languages"]:
                details = stats["language_details"][lang]
                lang_name = self._get_language_name(lang)
                lines.append(f"├── {lang_name} : {details['old_count']} URLs → Fallback /{self.default_fallback_lang}/")
            lines.append("")
        
        lines.extend([
            f"💡 Total : {stats['fallback_count']} redirections 302 générées",
            f"🎯 Cible principale : /{self.default_fallback_lang}/ (langue par défaut)"
        ])
        
        return "\n".join(lines)
    
    def _get_language_name(self, lang_code: str) -> str:
        """Convertit un code langue en nom lisible"""
        names = {
            'fr': '🇫🇷 Français',
            'en': '🇬🇧 Anglais',
            'de': '🇩🇪 Allemand', 
            'es': '🇪🇸 Espagnol',
            'it': '🇮🇹 Italien',
            'nl': '🇳🇱 Néerlandais'
        }
        return names.get(lang_code, f"🌐 {lang_code.upper()}")
    
    def set_default_fallback(self, language: str) -> None:
        """Modifie la langue de fallback par défaut"""
        self.default_fallback_lang = language
    
    def get_supported_fallback_languages(self) -> List[str]:
        """Retourne les langues supportées pour fallback"""
        return ['fr', 'en', 'de', 'es', 'it', 'nl']