"""
SmartRetry - Mécanisme de retry intelligent et resilient
US-2.2: En tant qu'utilisateur, je veux un scraper resilient qui retry intelligemment
"""

import time
import random
from typing import Callable, Any, Optional, Dict, Type
from urllib.parse import urlparse
from src.smart_input_config import RETRY_CONFIG


class SmartRetry:
    """Gestionnaire intelligent des retries avec backoff exponentiel"""
    
    def __init__(self):
        self.statistics = {
            'total_executions': 0,
            'total_retries': 0,
            'successful_executions': 0,
            'failed_executions': 0,
            'retry_reasons': {},
            'average_retry_count': 0.0
        }
        
        # Erreurs retriables par défaut
        self.retriable_errors = (
            ConnectionError,
            TimeoutError,
            OSError,  # Inclut les erreurs réseau
        )
        
        # Codes HTTP retriables
        self.retriable_http_codes = set(RETRY_CONFIG['retry_status_codes'])
    
    def execute_with_retry(self, 
                          func: Callable,
                          max_retries: int = None,
                          base_delay: float = None,
                          backoff_factor: float = None,
                          retry_condition: Optional[Callable] = None,
                          **kwargs) -> Any:
        """
        Exécute une fonction avec retry automatique
        
        Args:
            func: Fonction à exécuter
            max_retries: Nombre max de retries (défaut: config)
            base_delay: Délai de base en secondes (défaut: 1.0)
            backoff_factor: Facteur de backoff (défaut: config)
            retry_condition: Fonction personnalisée pour décider du retry
            **kwargs: Arguments passés à la fonction
            
        Returns:
            Résultat de la fonction
            
        Raises:
            Exception: Si toutes les tentatives échouent
        """
        max_retries = max_retries or RETRY_CONFIG['max_retries']
        base_delay = base_delay or 1.0
        backoff_factor = backoff_factor or RETRY_CONFIG['backoff_factor']
        
        self.statistics['total_executions'] += 1
        retry_count = 0
        
        while retry_count <= max_retries:
            try:
                result = func(**kwargs)
                
                # Succès !
                if retry_count == 0:
                    self.statistics['successful_executions'] += 1
                else:
                    self.statistics['total_retries'] += retry_count
                    self._update_average_retry_count()
                
                return result
                
            except Exception as e:
                # Vérifier si on doit retenter
                should_retry = self._should_retry(e, retry_count, max_retries, retry_condition)
                
                if not should_retry:
                    self.statistics['failed_executions'] += 1
                    self._track_retry_reason(type(e).__name__)
                    raise
                
                # Calculer le délai
                delay = self._calculate_delay(base_delay, backoff_factor, retry_count)
                
                # Attendre avant le retry
                self._sleep_with_jitter(delay)
                
                retry_count += 1
                self._track_retry_reason(type(e).__name__)
        
        # Si on arrive ici, toutes les tentatives ont échoué
        self.statistics['failed_executions'] += 1
        self.statistics['total_retries'] += retry_count
        self._update_average_retry_count()
        raise
    
    def execute_http_with_retry(self,
                               http_func: Callable,
                               max_retries: int = None,
                               **kwargs) -> Any:
        """
        Exécute une requête HTTP avec retry intelligent
        
        Args:
            http_func: Fonction qui retourne un objet Response
            max_retries: Nombre max de retries
            **kwargs: Arguments pour execute_with_retry
            
        Returns:
            Objet Response
        """
        def http_retry_condition(exception_or_response):
            # Si c'est une exception, utiliser la logique standard
            if isinstance(exception_or_response, Exception):
                return self._is_retriable_error(exception_or_response)
            
            # Si c'est une réponse HTTP, vérifier le status code
            if hasattr(exception_or_response, 'status_code'):
                return self._is_retriable_http_code(exception_or_response.status_code)
            
            return False
        
        def enhanced_http_func(**func_kwargs):
            response = http_func(**func_kwargs)
            
            # Vérifier si la réponse nécessite un retry
            if hasattr(response, 'status_code'):
                if self._is_retriable_http_code(response.status_code):
                    # Gérer le header Retry-After pour 429
                    if response.status_code == 429:
                        retry_after = self._get_retry_after_delay(response)
                        if retry_after:
                            time.sleep(retry_after)
                    
                    # Lever une exception pour déclencher le retry
                    raise ConnectionError(f"HTTP {response.status_code}")
            
            return response
        
        return self.execute_with_retry(
            enhanced_http_func,
            max_retries=max_retries,
            retry_condition=http_retry_condition,
            **kwargs
        )
    
    def _should_retry(self, 
                     exception: Exception, 
                     retry_count: int, 
                     max_retries: int,
                     custom_condition: Optional[Callable] = None) -> bool:
        """Détermine si on doit retenter après une exception"""
        
        # Si on a atteint le max de retries
        if retry_count >= max_retries:
            return False
        
        # Condition personnalisée
        if custom_condition:
            return custom_condition(exception)
        
        # Vérifier si l'erreur est retriable
        return self._is_retriable_error(exception)
    
    def _is_retriable_error(self, exception: Exception) -> bool:
        """Vérifie si une exception est retriable"""
        return isinstance(exception, self.retriable_errors)
    
    def _is_retriable_http_code(self, status_code: int) -> bool:
        """Vérifie si un code HTTP est retriable"""
        # Ne pas retenter les erreurs 4xx sauf 429 (rate limit)
        if 400 <= status_code < 500 and status_code != 429:
            return False
        
        return status_code in self.retriable_http_codes
    
    def _calculate_delay(self, base_delay: float, backoff_factor: float, retry_count: int) -> float:
        """Calcule le délai avec backoff exponentiel"""
        delay = base_delay * (backoff_factor ** retry_count)
        
        # Limiter le délai maximum à 60 secondes
        return min(delay, 60.0)
    
    def _sleep_with_jitter(self, delay: float):
        """Attendre avec un jitter aléatoire pour éviter le thundering herd"""
        # Ajouter ±25% de jitter
        jitter = delay * 0.25 * (random.random() - 0.5) * 2
        actual_delay = max(0.1, delay + jitter)
        time.sleep(actual_delay)
    
    def _get_retry_after_delay(self, response) -> Optional[float]:
        """Extrait le délai du header Retry-After"""
        retry_after = response.headers.get('Retry-After')
        if not retry_after:
            return None
        
        try:
            # Retry-After peut être en secondes ou une date
            return float(retry_after)
        except ValueError:
            # Si c'est une date, on utilise un délai par défaut
            return 60.0
    
    def _track_retry_reason(self, error_type: str):
        """Enregistre la raison du retry"""
        if error_type in self.statistics['retry_reasons']:
            self.statistics['retry_reasons'][error_type] += 1
        else:
            self.statistics['retry_reasons'][error_type] = 1
    
    def _update_average_retry_count(self):
        """Met à jour la moyenne des retries"""
        total_with_retries = self.statistics['total_executions'] - self.statistics['successful_executions']
        if total_with_retries > 0:
            self.statistics['average_retry_count'] = self.statistics['total_retries'] / total_with_retries
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Retourne les statistiques de retry
        
        Returns:
            Dictionnaire avec les statistiques
        """
        total_executions = self.statistics['total_executions']
        success_rate = 0.0
        if total_executions > 0:
            success_rate = self.statistics['successful_executions'] / total_executions
        
        return {
            'total_executions': total_executions,
            'total_retries': self.statistics['total_retries'],
            'successful_executions': self.statistics['successful_executions'],
            'failed_executions': self.statistics['failed_executions'],
            'success_rate': success_rate,
            'average_retry_count': self.statistics['average_retry_count'],
            'retry_reasons': self.statistics['retry_reasons'].copy(),
            'most_common_retry_reason': self._get_most_common_retry_reason()
        }
    
    def _get_most_common_retry_reason(self) -> Optional[str]:
        """Retourne la raison de retry la plus commune"""
        if not self.statistics['retry_reasons']:
            return None
        
        return max(self.statistics['retry_reasons'], 
                  key=self.statistics['retry_reasons'].get)
    
    def reset_statistics(self):
        """Remet à zéro les statistiques"""
        self.statistics = {
            'total_executions': 0,
            'total_retries': 0,
            'successful_executions': 0,
            'failed_executions': 0,
            'retry_reasons': {},
            'average_retry_count': 0.0
        }
    
    def configure_retriable_errors(self, error_types: tuple):
        """Configure les types d'erreurs retriables"""
        self.retriable_errors = error_types
    
    def configure_retriable_http_codes(self, status_codes: set):
        """Configure les codes HTTP retriables"""
        self.retriable_http_codes = status_codes