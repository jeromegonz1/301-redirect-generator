"""
Tests pour le mécanisme de retry intelligent
US-2.2: En tant qu'utilisateur, je veux un scraper resilient qui retry intelligemment
"""

import pytest
import time
from unittest.mock import Mock, patch
from src.smart_retry import SmartRetry


class TestSmartRetry:
    
    def setup_method(self):
        """Setup pour chaque test"""
        self.retry_manager = SmartRetry()
    
    def test_should_retry_on_failed_requests(self):
        """Test: doit retenter les requêtes échouées"""
        # Mock d'une fonction qui échoue puis réussit
        call_count = 0
        def failing_function():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ConnectionError("Connection failed")
            return "Success"
        
        result = self.retry_manager.execute_with_retry(failing_function)
        
        assert result == "Success"
        assert call_count == 3
    
    def test_should_use_exponential_backoff(self):
        """Test: doit utiliser un backoff exponentiel"""
        delays = []
        
        def mock_sleep(duration):
            delays.append(duration)
        
        with patch('time.sleep', side_effect=mock_sleep):
            def always_failing():
                raise ConnectionError("Always fails")
            
            with pytest.raises(ConnectionError):
                self.retry_manager.execute_with_retry(
                    always_failing,
                    max_retries=3,
                    base_delay=1.0
                )
        
        # Vérifier que les délais augmentent exponentiellement
        assert len(delays) == 3
        assert delays[0] >= 1.0
        assert delays[1] > delays[0]
        assert delays[2] > delays[1]
    
    def test_should_respect_max_retries(self):
        """Test: doit respecter le nombre maximum de tentatives"""
        call_count = 0
        def always_failing():
            nonlocal call_count
            call_count += 1
            raise ValueError("Always fails")
        
        with pytest.raises(ValueError):
            self.retry_manager.execute_with_retry(
                always_failing,
                max_retries=2
            )
        
        # Doit avoir essayé 3 fois (tentative initiale + 2 retries)
        assert call_count == 3
    
    def test_should_retry_only_retriable_errors(self):
        """Test: doit retenter seulement les erreurs retriables"""
        # Erreur retriable
        call_count_retriable = 0
        def retriable_error():
            nonlocal call_count_retriable
            call_count_retriable += 1
            raise ConnectionError("Network error")
        
        with pytest.raises(ConnectionError):
            self.retry_manager.execute_with_retry(retriable_error, max_retries=2)
        
        assert call_count_retriable == 3  # 1 + 2 retries
        
        # Erreur non-retriable
        call_count_non_retriable = 0
        def non_retriable_error():
            nonlocal call_count_non_retriable
            call_count_non_retriable += 1
            raise ValueError("Invalid input")
        
        with pytest.raises(ValueError):
            self.retry_manager.execute_with_retry(non_retriable_error, max_retries=2)
        
        assert call_count_non_retriable == 1  # Pas de retry
    
    def test_should_handle_http_status_codes(self):
        """Test: doit gérer les codes de statut HTTP"""
        # Mock response avec retry
        mock_response_fail = Mock()
        mock_response_fail.status_code = 503
        mock_response_fail.raise_for_status.side_effect = Exception("Service Unavailable")
        
        mock_response_success = Mock()
        mock_response_success.status_code = 200
        mock_response_success.raise_for_status.return_value = None
        
        call_count = 0
        def http_request():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                return mock_response_fail
            return mock_response_success
        
        result = self.retry_manager.execute_http_with_retry(http_request)
        
        assert result.status_code == 200
        assert call_count == 3
    
    def test_should_not_retry_4xx_errors(self):
        """Test: ne doit pas retenter les erreurs 4xx (sauf 429)"""
        call_count = 0
        def http_404():
            nonlocal call_count
            call_count += 1
            mock_response = Mock()
            mock_response.status_code = 404
            return mock_response
        
        result = self.retry_manager.execute_http_with_retry(http_404)
        
        # Ne doit pas avoir retenté
        assert call_count == 1
        assert result.status_code == 404
    
    def test_should_retry_429_rate_limit(self):
        """Test: doit retenter les erreurs 429 (rate limit)"""
        call_count = 0
        def rate_limited():
            nonlocal call_count
            call_count += 1
            mock_response = Mock()
            if call_count < 3:
                mock_response.status_code = 429
                mock_response.headers = {'Retry-After': '2'}
            else:
                mock_response.status_code = 200
            return mock_response
        
        result = self.retry_manager.execute_http_with_retry(rate_limited)
        
        assert result.status_code == 200
        assert call_count == 3
    
    def test_should_respect_retry_after_header(self):
        """Test: doit respecter le header Retry-After"""
        delays = []
        
        def mock_sleep(duration):
            delays.append(duration)
        
        with patch('time.sleep', side_effect=mock_sleep):
            def rate_limited_with_header():
                mock_response = Mock()
                mock_response.status_code = 429
                mock_response.headers = {'Retry-After': '5'}
                return mock_response
            
            result = self.retry_manager.execute_http_with_retry(
                rate_limited_with_header,
                max_retries=1
            )
        
        # Doit avoir attendu au moins 5 secondes
        assert len(delays) == 1
        assert delays[0] >= 5.0
    
    def test_should_provide_retry_statistics(self):
        """Test: doit fournir des statistiques de retry"""
        # Exécuter quelques requêtes avec retry
        def sometimes_failing():
            if hasattr(sometimes_failing, 'count'):
                sometimes_failing.count += 1
            else:
                sometimes_failing.count = 1
            
            if sometimes_failing.count <= 2:
                raise ConnectionError("Fail")
            return "Success"
        
        self.retry_manager.execute_with_retry(sometimes_failing)
        
        stats = self.retry_manager.get_statistics()
        
        assert stats['total_executions'] >= 1
        assert stats['total_retries'] >= 2
        assert stats['success_rate'] > 0
    
    def test_should_handle_timeout_errors(self):
        """Test: doit gérer les erreurs de timeout"""
        call_count = 0
        def timeout_function():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise TimeoutError("Request timeout")
            return "Success after timeout"
        
        result = self.retry_manager.execute_with_retry(timeout_function)
        
        assert result == "Success after timeout"
        assert call_count == 3
    
    def test_should_allow_custom_retry_conditions(self):
        """Test: doit permettre des conditions de retry personnalisées"""
        def custom_condition(exception):
            return isinstance(exception, ValueError) and "retry" in str(exception)
        
        call_count = 0
        def custom_failing():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("Please retry this")
            return "Custom success"
        
        result = self.retry_manager.execute_with_retry(
            custom_failing,
            retry_condition=custom_condition
        )
        
        assert result == "Custom success"
        assert call_count == 3
    
    def test_should_track_retry_reasons(self):
        """Test: doit tracker les raisons de retry"""
        def various_errors():
            if not hasattr(various_errors, 'attempt'):
                various_errors.attempt = 0
            various_errors.attempt += 1
            
            if various_errors.attempt == 1:
                raise ConnectionError("Network")
            elif various_errors.attempt == 2:
                raise TimeoutError("Timeout")
            else:
                return "Success"
        
        result = self.retry_manager.execute_with_retry(various_errors)
        
        stats = self.retry_manager.get_statistics()
        assert 'retry_reasons' in stats
        assert 'ConnectionError' in stats['retry_reasons']
        assert 'TimeoutError' in stats['retry_reasons']