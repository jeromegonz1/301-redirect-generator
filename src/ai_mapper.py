"""
Mapper IA pour matching sémantique entre URLs (US009)
Utilise GPT-3.5-turbo pour correspondances intelligentes
"""

import json
import time
import math
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from openai import OpenAI


class AIMatchingError(Exception):
    """Exception personnalisée pour erreurs de matching IA"""
    pass


@dataclass
class MatchResult:
    """Résultat d'un matching IA"""
    correspondances: List[Dict[str, Any]]
    non_matchees: List[str]
    
    def get_confidence_stats(self) -> Dict[str, float]:
        """Calcule les statistiques de confidence"""
        if not self.correspondances:
            return {"moyenne": 0.0, "min": 0.0, "max": 0.0}
        
        confidences = [m["confidence"] for m in self.correspondances]
        return {
            "moyenne": sum(confidences) / len(confidences),
            "min": min(confidences),
            "max": max(confidences)
        }


class AIMapper:
    """Mapper IA pour correspondances sémantiques entre URLs"""
    
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo", 
                 temperature: float = 0.1, max_retries: int = 3, 
                 chunk_size: int = 50):
        """
        Initialise le mapper IA
        
        Args:
            api_key: Clé API OpenAI
            model: Modèle à utiliser (gpt-3.5-turbo par défaut)
            temperature: Température pour le sampling (0.1 = très déterministe)
            max_retries: Nombre maximum de tentatives en cas d'erreur
            chunk_size: Taille des lots d'URLs (50 par défaut)
        """
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.max_retries = max_retries
        self.client = OpenAI(api_key=api_key)
        
        # Configuration de chunking
        self.chunk_size = chunk_size
        self.max_tokens = 4000
        
        # Coûts approximatifs (USD pour 1K tokens)
        self.cost_per_1k_input = 0.0015  # GPT-3.5-turbo input
        self.cost_per_1k_output = 0.002  # GPT-3.5-turbo output
    
    def match_urls(self, old_urls: List[str], new_urls: List[str], 
                   contexte_metier: str = "", langue: str = "fr",
                   min_confidence: float = 0.7) -> MatchResult:
        """
        Effectue le matching sémantique entre deux listes d'URLs
        
        Args:
            old_urls: URLs de l'ancien site
            new_urls: URLs du nouveau site
            contexte_metier: Instructions contextuelles du chef de projet
            langue: Langue pour optimiser le prompt
            min_confidence: Seuil minimum de confidence
            
        Returns:
            Résultat du matching avec correspondances et non-matchées
        """
        if not old_urls or not new_urls:
            return MatchResult(correspondances=[], non_matchees=old_urls)
        
        # Chunking pour gérer les gros volumes
        chunks = self._create_chunks(old_urls, new_urls, self.chunk_size)
        
        all_correspondances = []
        all_non_matchees = []
        
        for chunk in chunks:
            chunk_result = self._match_chunk(
                chunk["old_urls"], 
                chunk["new_urls"],
                contexte_metier, 
                langue
            )
            
            # Filtrage par confidence
            valid_matches = [
                match for match in chunk_result.correspondances 
                if match.get("confidence", 0) >= min_confidence
            ]
            
            # URLs non matchées = rejetées par confidence + explicitement non matchées
            rejected_by_confidence = [
                match["ancienne"] for match in chunk_result.correspondances
                if match.get("confidence", 0) < min_confidence
            ]
            
            all_correspondances.extend(valid_matches)
            all_non_matchees.extend(chunk_result.non_matchees)
            all_non_matchees.extend(rejected_by_confidence)
        
        return MatchResult(
            correspondances=all_correspondances,
            non_matchees=all_non_matchees
        )
    
    def _match_chunk(self, old_urls: List[str], new_urls: List[str],
                     contexte_metier: str, langue: str) -> MatchResult:
        """Traite un chunk d'URLs avec retry automatique"""
        
        for attempt in range(self.max_retries):
            try:
                # Construction du prompt
                prompt = self._build_prompt(old_urls, new_urls, contexte_metier, langue)
                
                # Appel à l'API OpenAI
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system", 
                            "content": self._get_system_prompt(contexte_metier)
                        },
                        {"role": "user", "content": prompt}
                    ],
                    temperature=self.temperature,
                    max_tokens=self.max_tokens
                )
                
                # Parse la réponse
                content = response.choices[0].message.content
                result_data = self._parse_ai_response(content)
                
                return MatchResult(
                    correspondances=result_data.get("correspondances", []),
                    non_matchees=result_data.get("non_matchees", [])
                )
                
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise AIMatchingError(f"Échec du matching IA après {self.max_retries} tentatives: {e}")
                
                # Délai exponentiel entre les tentatives
                time.sleep(2 ** attempt)
    
    def _get_system_prompt(self, contexte_metier: str) -> str:
        """Construit le prompt système avec contexte métier"""
        
        base_prompt = """Tu es un expert en redirections 301 pour des refontes de sites web.
Ton rôle est d'associer chaque ancienne URL à la nouvelle URL la plus pertinente sémantiquement.

Règles :
- Analyse le sens et le contenu de chaque URL
- Une ancienne URL = une seule nouvelle URL maximum
- Score de confidence entre 0.0 et 1.0
- Si confidence < 0.7, placer dans "non_matchees"
- Réponse obligatoire en JSON valide
- Format : {"correspondances": [...], "non_matchees": [...]}"""
        
        if contexte_metier.strip():
            base_prompt += f"""

CONTEXTE MÉTIER FOURNI PAR LE CHEF DE PROJET :
{contexte_metier}

Utilise ce contexte pour comprendre :
- Les changements de terminologie
- La nouvelle structure éditoriale  
- Les langues actives/inactives
- Les priorités SEO du projet

Priorise ABSOLUMENT les informations du contexte métier dans tes décisions."""
        
        return base_prompt
    
    def _build_prompt(self, old_urls: List[str], new_urls: List[str], 
                     contexte_metier: str = "", langue: str = "fr") -> str:
        """Construit le prompt utilisateur"""
        
        prompt_parts = []
        
        # Ajouter le contexte métier au début du prompt si fourni
        if contexte_metier.strip():
            prompt_parts.append(f"""CONTEXTE MÉTIER :
{contexte_metier}

""")
        
        prompt_parts.append(f"""ANCIENNES URLS ({len(old_urls)}):
{chr(10).join(old_urls)}

NOUVELLES URLS ({len(new_urls)}):
{chr(10).join(new_urls)}

LANGUE PRINCIPALE : {langue}

Associe chaque ancienne URL à la meilleure nouvelle URL.
Réponse en JSON avec cette structure exacte :
{{
    "correspondances": [
        {{
            "ancienne": "URL_ancienne",
            "nouvelle": "URL_nouvelle",
            "confidence": 0.85,
            "raison": "Explication courte"
        }}
    ],
    "non_matchees": ["URL_sans_correspondance"]
}}""")
        
        return "".join(prompt_parts)
    
    def _parse_ai_response(self, response: str) -> Dict[str, Any]:
        """Parse la réponse JSON de l'IA avec gestion d'erreurs"""
        try:
            # Nettoie la réponse (enlève markdown, espaces, etc.)
            cleaned = response.strip()
            if cleaned.startswith("```"):
                # Enlève les blocs de code markdown
                lines = cleaned.split("\n")
                cleaned = "\n".join(line for line in lines if not line.startswith("```"))
            
            # Parse le JSON
            data = json.loads(cleaned)
            
            # Validation de la structure
            if not isinstance(data, dict):
                raise ValueError("La réponse n'est pas un objet JSON")
            
            if "correspondances" not in data or "non_matchees" not in data:
                raise ValueError("Structure JSON invalide")
            
            return data
            
        except (json.JSONDecodeError, ValueError) as e:
            raise AIMatchingError(f"Impossible de parser la réponse IA: {e}")
    
    def _create_chunks(self, old_urls: List[str], new_urls: List[str], 
                      chunk_size: int) -> List[Dict[str, List[str]]]:
        """Découpe les URLs en chunks pour traitement par lots"""
        
        chunks = []
        
        for i in range(0, len(old_urls), chunk_size):
            chunk_old = old_urls[i:i + chunk_size]
            
            # Pour les nouvelles URLs, on prend tout (ou un échantillon si trop gros)
            chunk_new = new_urls
            if len(new_urls) > 200:  # Limite pour éviter les prompts trop longs
                chunk_new = new_urls[:200]
            
            chunks.append({
                "old_urls": chunk_old,
                "new_urls": chunk_new
            })
        
        return chunks
    
    def estimate_cost(self, old_urls: List[str], new_urls: List[str],
                     contexte_metier: str = "") -> float:
        """
        Estime le coût approximatif du matching
        
        Returns:
            Coût estimé en USD
        """
        # Calcul approximatif des tokens
        total_chars = sum(len(url) for url in old_urls + new_urls)
        total_chars += len(contexte_metier)
        total_chars += 1000  # Overhead du prompt système
        
        # Approximation : 4 caractères = 1 token
        estimated_input_tokens = total_chars / 4
        estimated_output_tokens = len(old_urls) * 50  # ~50 tokens par correspondance
        
        # Calcul du coût
        input_cost = (estimated_input_tokens / 1000) * self.cost_per_1k_input
        output_cost = (estimated_output_tokens / 1000) * self.cost_per_1k_output
        
        return round(input_cost + output_cost, 4)
    
    def get_model_info(self) -> Dict[str, Any]:
        """Retourne les informations sur le modèle configuré"""
        return {
            "model": self.model,
            "temperature": self.temperature,
            "chunk_size": self.chunk_size,
            "max_tokens": self.max_tokens,
            "max_retries": self.max_retries
        }