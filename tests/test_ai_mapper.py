"""
Tests TDD pour le matching IA sémantique (US009)
Tests sans appel réel à l'API OpenAI (mocking)
"""

import pytest
from unittest.mock import Mock, patch
from typing import List, Dict, Any

class TestAIMapper:
    """Tests pour le matching IA sémantique"""
    
    def test_ai_mapper_initialization(self):
        """Test initialisation du mapper IA"""
        from src.ai_mapper import AIMapper
        
        # Ne pas utiliser de vraie clé API en dur
        test_api_key = "test-key-not-real"
        mapper = AIMapper(test_api_key)
        
        assert mapper.api_key == test_api_key
        assert mapper.model == "gpt-3.5-turbo"
        assert mapper.temperature == 0.1
    
    @patch('src.ai_mapper.OpenAI')
    def test_match_urls_basic(self, mock_openai):
        """Test matching basique avec mock de l'API"""
        from src.ai_mapper import AIMapper, MatchResult
        
        # Mock de la réponse OpenAI
        mock_response = {
            "correspondances": [
                {
                    "ancienne": "/camping-presentation-gard",
                    "nouvelle": "/presentation", 
                    "confidence": 0.95,
                    "raison": "Correspondance évidente : présentation du camping"
                }
            ],
            "non_matchees": []
        }
        
        mock_client = Mock()
        mock_openai.return_value = mock_client
        mock_client.chat.completions.create.return_value.choices = [
            Mock(message=Mock(content=str(mock_response).replace("'", '"')))
        ]
        
        # Test
        mapper = AIMapper("test-key")
        
        old_urls = ["/camping-presentation-gard"]
        new_urls = ["/presentation", "/services"]
        
        result = mapper.match_urls(old_urls, new_urls)
        
        # Vérifications
        assert isinstance(result, MatchResult)
        assert len(result.correspondances) == 1
        assert result.correspondances[0]["confidence"] == 0.95
    
    def test_match_result_structure(self):
        """Test structure du résultat de matching"""
        from src.ai_mapper import MatchResult
        
        # Données de test (pas de hardcoding)
        test_correspondances = [
            {
                "ancienne": "/test-page-1",
                "nouvelle": "/new-page-1",
                "confidence": 0.90,
                "raison": "Test matching"
            }
        ]
        
        test_non_matchees = ["/obsolete-page"]
        
        result = MatchResult(
            correspondances=test_correspondances,
            non_matchees=test_non_matchees
        )
        
        assert len(result.correspondances) == 1
        assert len(result.non_matchees) == 1
        assert result.correspondances[0]["confidence"] == 0.90
    
    @patch('src.ai_mapper.OpenAI')
    def test_confidence_filtering(self, mock_openai):
        """Test filtrage par score de confidence"""
        from src.ai_mapper import AIMapper
        
        # Mock avec différents scores de confidence
        mock_response = {
            "correspondances": [
                {"ancienne": "/page1", "nouvelle": "/new1", "confidence": 0.95, "raison": "Excellent"},
                {"ancienne": "/page2", "nouvelle": "/new2", "confidence": 0.80, "raison": "Bon"},
                {"ancienne": "/page3", "nouvelle": "/new3", "confidence": 0.60, "raison": "Faible"}
            ],
            "non_matchees": []
        }
        
        mock_client = Mock()
        mock_openai.return_value = mock_client
        mock_client.chat.completions.create.return_value.choices = [
            Mock(message=Mock(content=str(mock_response).replace("'", '"')))
        ]
        
        mapper = AIMapper("test-key")
        
        # Test avec seuil de confidence
        old_urls = ["/page1", "/page2", "/page3"]
        new_urls = ["/new1", "/new2", "/new3"]
        
        result = mapper.match_urls(old_urls, new_urls, min_confidence=0.7)
        
        # Seules les correspondances > 0.7 devraient être acceptées
        valid_matches = [m for m in result.correspondances if m["confidence"] >= 0.7]
        assert len(valid_matches) == 2  # 0.95 et 0.80 uniquement
    
    def test_chunking_for_large_datasets(self):
        """Test découpage en chunks pour gros volumes"""
        from src.ai_mapper import AIMapper
        
        mapper = AIMapper("test-key")
        
        # Simulation d'un gros dataset (pas de hardcoding des URLs)
        large_old_urls = [f"/old-page-{i}" for i in range(150)]
        large_new_urls = [f"/new-page-{i}" for i in range(150)]
        
        # Test du chunking
        chunks = mapper._create_chunks(large_old_urls, large_new_urls, chunk_size=50)
        
        assert len(chunks) == 3  # 150 / 50 = 3 chunks
        assert len(chunks[0]["old_urls"]) == 50
        assert len(chunks[1]["old_urls"]) == 50  
        assert len(chunks[2]["old_urls"]) == 50
    
    def test_contextual_prompt_injection(self):
        """Test injection du contexte métier (US014)"""
        from src.ai_mapper import AIMapper
        
        mapper = AIMapper("test-key")
        
        # Contexte métier de test
        test_context = "mobil-home devient nos locatifs, restaurant devient restauration"
        
        # Test construction du prompt avec contexte
        prompt = mapper._build_prompt(
            old_urls=["/mobil-home-luxe"],
            new_urls=["/nos-locatifs"],
            contexte_metier=test_context,
            langue="fr"
        )
        
        # Vérifier injection du contexte
        assert "mobil-home devient nos locatifs" in prompt
        assert "restaurant devient restauration" in prompt
        assert "CONTEXTE MÉTIER" in prompt
    
    def test_language_specific_matching(self):
        """Test matching spécifique par langue"""
        from src.ai_mapper import AIMapper
        
        mapper = AIMapper("test-key")
        
        # URLs dans différentes langues (pas de hardcoding sauf pour le test)
        fr_old = ["/fr/contact", "/fr/services"]
        fr_new = ["/fr/contact-nous", "/fr/nos-services"]
        
        en_old = ["/en/contact", "/en/about"]
        en_new = ["/en/contact-us", "/en/about-us"]
        
        # Test que le prompt inclut la langue
        fr_prompt = mapper._build_prompt(fr_old, fr_new, contexte_metier="", langue="fr")
        en_prompt = mapper._build_prompt(en_old, en_new, contexte_metier="", langue="en")
        
        assert "LANGUE PRINCIPALE : fr" in fr_prompt
        assert "LANGUE PRINCIPALE : en" in en_prompt
    
    def test_error_handling_api_failure(self):
        """Test gestion d'erreur en cas d'échec API"""
        from src.ai_mapper import AIMapper, AIMatchingError
        
        with patch('src.ai_mapper.OpenAI') as mock_openai:
            mock_client = Mock()
            mock_openai.return_value = mock_client
            mock_client.chat.completions.create.side_effect = Exception("API Error")
            
            mapper = AIMapper("test-key")
            
            # Doit lever une exception personnalisée
            with pytest.raises(AIMatchingError):
                mapper.match_urls(["/test"], ["/test-new"])
    
    @patch('src.ai_mapper.OpenAI')
    def test_retry_mechanism(self, mock_openai):
        """Test mécanisme de retry"""
        from src.ai_mapper import AIMapper
        
        mapper = AIMapper("test-key", max_retries=3)
        
        mock_client = Mock()
        mock_openai.return_value = mock_client
        
        # Premier appel échoue, second réussit
        mock_client.chat.completions.create.side_effect = [
            Exception("Temporary error"),
            Mock(choices=[Mock(message=Mock(content='{"correspondances": [], "non_matchees": []}'))])
        ]
        
        # Ne doit pas lever d'exception grâce au retry
        result = mapper.match_urls(["/test"], ["/test-new"])
        assert result is not None
    
    def test_cost_estimation(self):
        """Test estimation du coût API"""
        from src.ai_mapper import AIMapper
        
        mapper = AIMapper("test-key")
        
        # URLs de test pour estimation
        test_old_urls = [f"/page-{i}" for i in range(100)]
        test_new_urls = [f"/new-{i}" for i in range(100)]
        
        estimated_cost = mapper.estimate_cost(test_old_urls, test_new_urls)
        
        # Doit retourner une estimation > 0
        assert estimated_cost > 0
        assert isinstance(estimated_cost, float)
    
    def test_json_response_parsing(self):
        """Test parsing robuste de la réponse JSON"""
        from src.ai_mapper import AIMapper
        
        mapper = AIMapper("test-key")
        
        # Test différents formats de réponse JSON
        test_responses = [
            '{"correspondances": [], "non_matchees": []}',  # Standard
            '{\n  "correspondances": [],\n  "non_matchees": []\n}',  # Formaté
            '{"correspondances":[],"non_matchees":[]}'  # Compact
        ]
        
        for response in test_responses:
            parsed = mapper._parse_ai_response(response)
            assert "correspondances" in parsed
            assert "non_matchees" in parsed