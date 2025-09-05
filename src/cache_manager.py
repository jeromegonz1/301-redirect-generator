"""
Gestionnaire de cache pour éviter les appels API GPT répétés
Économise les coûts en sauvegardant les résultats des tests
"""

import json
import hashlib
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path


class CacheManager:
    """Gestionnaire de cache pour les résultats GPT et fichiers .htaccess"""
    
    def __init__(self, cache_dir: str = "outputs"):
        """
        Initialise le gestionnaire de cache
        
        Args:
            cache_dir: Répertoire de cache (par défaut: outputs)
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        
        # Sous-dossiers pour organiser
        self.gpt_cache_dir = self.cache_dir / "gpt_cache"
        self.htaccess_dir = self.cache_dir / "htaccess_files" 
        
        self.gpt_cache_dir.mkdir(exist_ok=True)
        self.htaccess_dir.mkdir(exist_ok=True)
    
    def _generate_cache_key(self, old_urls: List[str], new_urls: List[str], 
                           contexte_metier: str = "", temperature: float = 0.1) -> str:
        """
        Génère une clé de cache basée sur les URLs et paramètres
        
        Args:
            old_urls: URLs anciennes
            new_urls: URLs nouvelles
            contexte_metier: Contexte métier
            temperature: Température IA
            
        Returns:
            Clé de cache unique
        """
        # Crée un hash basé sur le contenu et les paramètres
        content = {
            "old_urls": sorted(old_urls),  # Trié pour cohérence
            "new_urls": sorted(new_urls),
            "contexte_metier": contexte_metier.strip(),
            "temperature": temperature
        }
        
        content_str = json.dumps(content, sort_keys=True)
        hash_obj = hashlib.md5(content_str.encode())
        return hash_obj.hexdigest()[:12]  # 12 premiers caractères
    
    def get_gpt_cache(self, old_urls: List[str], new_urls: List[str],
                      contexte_metier: str = "", temperature: float = 0.1) -> Optional[Dict[str, Any]]:
        """
        Récupère les résultats GPT depuis le cache
        
        Returns:
            Données mises en cache ou None si pas trouvé
        """
        cache_key = self._generate_cache_key(old_urls, new_urls, contexte_metier, temperature)
        cache_file = self.gpt_cache_dir / f"gpt_results_{cache_key}.json"
        
        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                # Cache corrompu, on l'ignore
                return None
        
        return None
    
    def save_gpt_cache(self, old_urls: List[str], new_urls: List[str],
                       contexte_metier: str, temperature: float,
                       gpt_results: Dict[str, Any]) -> str:
        """
        Sauvegarde les résultats GPT dans le cache
        
        Returns:
            Nom du fichier de cache créé
        """
        cache_key = self._generate_cache_key(old_urls, new_urls, contexte_metier, temperature)
        cache_file = self.gpt_cache_dir / f"gpt_results_{cache_key}.json"
        
        cache_data = {
            "timestamp": datetime.now().isoformat(),
            "cache_key": cache_key,
            "old_urls_count": len(old_urls),
            "new_urls_count": len(new_urls),
            "contexte_metier": contexte_metier,
            "temperature": temperature,
            "results": gpt_results
        }
        
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, indent=2, ensure_ascii=False)
        
        return cache_file.name
    
    def save_htaccess_file(self, htaccess_content: str, old_urls: List[str], 
                          new_urls: List[str], suffix: str = "") -> str:
        """
        Sauvegarde le fichier .htaccess généré
        
        Args:
            htaccess_content: Contenu du fichier .htaccess
            old_urls: URLs anciennes (pour générer un nom unique)
            new_urls: URLs nouvelles
            suffix: Suffixe optionnel pour le nom de fichier
            
        Returns:
            Chemin du fichier sauvegardé
        """
        # Génère un nom de fichier basé sur timestamp et hash
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        cache_key = self._generate_cache_key(old_urls, new_urls)
        
        filename = f"htaccess_{timestamp}_{cache_key}"
        if suffix:
            filename += f"_{suffix}"
        filename += ".txt"
        
        file_path = self.htaccess_dir / filename
        
        # Ajoute des métadonnées en en-tête
        header = f"""# Fichier .htaccess généré par 301 Redirect Generator
# Date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
# URLs anciennes: {len(old_urls)}
# URLs nouvelles: {len(new_urls)}
# Cache key: {cache_key}

"""
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(header + htaccess_content)
        
        return str(file_path)
    
    def list_cached_results(self) -> List[Dict[str, Any]]:
        """
        Liste tous les résultats mis en cache
        
        Returns:
            Liste des métadonnées des caches disponibles
        """
        cached_files = []
        
        for cache_file in self.gpt_cache_dir.glob("gpt_results_*.json"):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                cached_files.append({
                    "file": cache_file.name,
                    "cache_key": data.get("cache_key", "unknown"),
                    "timestamp": data.get("timestamp", "unknown"),
                    "old_urls_count": data.get("old_urls_count", 0),
                    "new_urls_count": data.get("new_urls_count", 0),
                    "contexte_metier": data.get("contexte_metier", "")[:100] + "..." if len(data.get("contexte_metier", "")) > 100 else data.get("contexte_metier", "")
                })
            except (json.JSONDecodeError, KeyError):
                continue
        
        # Trie par timestamp (plus récent en premier)
        cached_files.sort(key=lambda x: x["timestamp"], reverse=True)
        return cached_files
    
    def clear_old_cache(self, days: int = 7) -> int:
        """
        Nettoie les anciens fichiers de cache
        
        Args:
            days: Nombre de jours à conserver
            
        Returns:
            Nombre de fichiers supprimés
        """
        from datetime import timedelta
        
        cutoff_date = datetime.now() - timedelta(days=days)
        deleted_count = 0
        
        for cache_file in self.gpt_cache_dir.glob("gpt_results_*.json"):
            try:
                file_time = datetime.fromtimestamp(cache_file.stat().st_mtime)
                if file_time < cutoff_date:
                    cache_file.unlink()
                    deleted_count += 1
            except (OSError, ValueError):
                continue
        
        return deleted_count
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Retourne des statistiques sur le cache
        
        Returns:
            Statistiques du cache
        """
        gpt_files = list(self.gpt_cache_dir.glob("gpt_results_*.json"))
        htaccess_files = list(self.htaccess_dir.glob("htaccess_*.txt"))
        
        total_size = sum(f.stat().st_size for f in gpt_files + htaccess_files)
        
        return {
            "gpt_cache_files": len(gpt_files),
            "htaccess_files": len(htaccess_files),
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "cache_dir": str(self.cache_dir)
        }