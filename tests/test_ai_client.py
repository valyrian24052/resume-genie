"""Tests for AI client functionality."""

import pytest
from unittest.mock import Mock, patch, MagicMock
import requests
from requests.exceptions import Timeout, ConnectionError, RequestException

from ai.ai_client import AIClient, AIResponse


class TestAIClient:
    """Test cases for AIClient class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.api_key = "test-api-key"
        self.base_url = "https://api.test.com/v1"
        self.client = AIClient(api_key=self.api_key, base_url=self.base_url)
    
    def test_init_configuration(self):
        """Test client initialization with configuration."""
        assert self.client.api_key == self.api_key
        assert self.client.base_url == "https://api.test.com/v1"
        assert self.client.timeout == 30
        assert self.client.max_retries == 3
        
        # Test custom configuration
        custom_client = AIClient(
            api_key="custom-key",
            base_url="https://custom.api.com/v2/",
            timeout=60,
            max_retries=5
        )
        assert custom_client.base_url == "https://custom.api.com/v2"
        assert custom_client.timeout == 60
        assert custom_client.max_retries == 5
    
    @patch('requests.Session.post')
    def test_customize_content_success(self, mock_post):
        """Test successful content customization."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [
                {"message": {"content": "Customized content here"}}
            ]
        }
        mock_post.return_value = mock_response
        
        result = self.client.customize_content(
            prompt="Test prompt",
            content="Original content",
            job_context="Job context"
        )
        
        assert result.success is True
        assert result.content == "Customized content here"
        assert result.error_message is None
        
        # Verify the request was made correctly
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args[0][0] == f"{self.base_url}/chat/completions"
        
        payload = call_args[1]['json']
        assert payload['model'] == 'gpt-3.5-turbo'
        assert len(payload['messages']) == 2
        assert payload['messages'][0]['role'] == 'system'
        assert payload['messages'][0]['content'] == 'Test prompt'
        assert 'Job Context: Job context' in payload['messages'][1]['content']
        assert 'Original Content: Original content' in payload['messages'][1]['content']
    
    @patch('requests.Session.post')
    def test_customize_content_api_error(self, mock_post):
        """Test handling of API error responses."""
        # Mock error response
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        mock_post.return_value = mock_response
        
        result = self.client.customize_content(
            prompt="Test prompt",
            content="Original content",
            job_context="Job context"
        )
        
        assert result.success is False
        assert result.content == ""
        assert "AI endpoint returned status 400" in result.error_message
        assert result.status_code == 400
    
    @patch('requests.Session.post')
    def test_customize_content_invalid_response_format(self, mock_post):
        """Test handling of invalid response format."""
        # Mock response with missing choices
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"error": "No choices"}
        mock_post.return_value = mock_response
        
        result = self.client.customize_content(
            prompt="Test prompt",
            content="Original content",
            job_context="Job context"
        )
        
        assert result.success is False
        assert result.content == ""
        assert "Invalid response format" in result.error_message
    
    @patch('requests.Session.post')
    def test_customize_content_timeout(self, mock_post):
        """Test handling of request timeout."""
        mock_post.side_effect = Timeout("Request timed out")
        
        result = self.client.customize_content(
            prompt="Test prompt",
            content="Original content",
            job_context="Job context"
        )
        
        assert result.success is False
        assert result.content == ""
        assert "Request timeout" in result.error_message
    
    @patch('requests.Session.post')
    def test_customize_content_connection_error(self, mock_post):
        """Test handling of connection errors."""
        mock_post.side_effect = ConnectionError("Connection failed")
        
        result = self.client.customize_content(
            prompt="Test prompt",
            content="Original content",
            job_context="Job context"
        )
        
        assert result.success is False
        assert result.content == ""
        assert "Failed to connect to AI endpoint" in result.error_message
    
    @patch('requests.Session.post')
    def test_customize_content_json_decode_error(self, mock_post):
        """Test handling of JSON decode errors."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_post.return_value = mock_response
        
        result = self.client.customize_content(
            prompt="Test prompt",
            content="Original content",
            job_context="Job context"
        )
        
        assert result.success is False
        assert result.content == ""
        assert "Failed to parse AI response as JSON" in result.error_message
    
    @patch('requests.Session.post')
    def test_is_available_success(self, mock_post):
        """Test successful availability check."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        assert self.client.is_available() is True
    
    @patch('requests.Session.post')
    def test_is_available_failure(self, mock_post):
        """Test failed availability check."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_post.return_value = mock_response
        
        assert self.client.is_available() is False
    
    @patch('requests.Session.post')
    def test_is_available_exception(self, mock_post):
        """Test availability check with exception."""
        mock_post.side_effect = ConnectionError("Connection failed")
        
        assert self.client.is_available() is False


class TestAIResponse:
    """Test cases for AIResponse dataclass."""
    
    def test_success_response(self):
        """Test successful response creation."""
        response = AIResponse(success=True, content="Test content")
        
        assert response.success is True
        assert response.content == "Test content"
        assert response.error_message is None
        assert response.status_code is None
    
    def test_error_response(self):
        """Test error response creation."""
        response = AIResponse(
            success=False,
            content="",
            error_message="Test error",
            status_code=400
        )
        
        assert response.success is False
        assert response.content == ""
        assert response.error_message == "Test error"
        assert response.status_code == 400