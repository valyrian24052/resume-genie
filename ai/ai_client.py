"""HTTP client for AI endpoint communication."""

import json
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


logger = logging.getLogger(__name__)


@dataclass
class AIResponse:
    """Response from AI endpoint."""
    success: bool
    content: str
    error_message: Optional[str] = None
    status_code: Optional[int] = None


class AIClient:
    """HTTP client for communicating with AI endpoints."""
    
    def __init__(self, api_key: str, base_url: str = "https://api.openai.com/v1", 
                 timeout: int = 30, max_retries: int = 3):
        """Initialize AI client with configuration.
        
        Args:
            api_key: API key for authentication
            base_url: Base URL for AI API endpoints
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.max_retries = max_retries
        
        # Configure session with retry strategy
        self.session = requests.Session()
        retry_strategy = Retry(
            total=max_retries,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "POST"],
            backoff_factor=1
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Set default headers
        self.session.headers.update({
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        })
    
    def customize_content_with_params(self, prompt: str, context: str, 
                                    model_params: Dict[str, Any]) -> AIResponse:
        """Request content customization with custom model parameters.
        
        Args:
            prompt: System prompt for customization task
            context: Full context including job profile and content
            model_params: Model parameters (model, max_tokens, temperature, etc.)
            
        Returns:
            AIResponse with customized content or error information
        """
        try:
            payload = {
                "model": model_params.get("model", "gpt-4o-mini"),
                "messages": [
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": context}
                ],
                "max_tokens": model_params.get("max_tokens", 1000),
                "temperature": model_params.get("temperature", 0.7)
            }
            
            logger.debug(f"Sending AI request to {self.base_url}/chat/completions")
            response = self.session.post(
                f"{self.base_url}/chat/completions",
                json=payload,
                timeout=model_params.get("timeout", self.timeout)
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'choices' in data and len(data['choices']) > 0:
                    customized_content = data['choices'][0]['message']['content'].strip()
                    logger.info("Successfully received AI customization response")
                    return AIResponse(success=True, content=customized_content)
                else:
                    error_msg = "Invalid response format from AI endpoint"
                    logger.error(error_msg)
                    return AIResponse(success=False, content="", error_message=error_msg, status_code=response.status_code)
            else:
                error_msg = f"AI endpoint returned status {response.status_code}: {response.text}"
                logger.error(error_msg)
                return AIResponse(success=False, content="", error_message=error_msg, status_code=response.status_code)
                
        except requests.exceptions.Timeout:
            timeout_val = model_params.get("timeout", self.timeout)
            error_msg = f"Request timeout after {timeout_val} seconds"
            logger.error(error_msg)
            return AIResponse(success=False, content="", error_message=error_msg)
        
        except requests.exceptions.ConnectionError:
            error_msg = "Failed to connect to AI endpoint"
            logger.error(error_msg)
            return AIResponse(success=False, content="", error_message=error_msg)
        
        except requests.exceptions.RequestException as e:
            error_msg = f"Request failed: {str(e)}"
            logger.error(error_msg)
            return AIResponse(success=False, content="", error_message=error_msg)
        
        except (json.JSONDecodeError, ValueError):
            error_msg = "Failed to parse AI response as JSON"
            logger.error(error_msg)
            return AIResponse(success=False, content="", error_message=error_msg)
        
        except Exception as e:
            error_msg = f"Unexpected error during AI request: {str(e)}"
            logger.error(error_msg)
            return AIResponse(success=False, content="", error_message=error_msg)

    def customize_content(self, prompt: str, content: str, job_context: str) -> AIResponse:
        """Request content customization from AI endpoint.
        
        Args:
            prompt: System prompt for customization task
            content: Original content to customize
            job_context: Job profile context for customization
            
        Returns:
            AIResponse with customized content or error information
        """
        try:
            payload = {
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": f"Job Context: {job_context}\n\nOriginal Content: {content}"}
                ],
                "max_tokens": 1000,
                "temperature": 0.7
            }
            
            logger.debug(f"Sending AI request to {self.base_url}/chat/completions")
            response = self.session.post(
                f"{self.base_url}/chat/completions",
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'choices' in data and len(data['choices']) > 0:
                    customized_content = data['choices'][0]['message']['content'].strip()
                    logger.info("Successfully received AI customization response")
                    return AIResponse(success=True, content=customized_content)
                else:
                    error_msg = "Invalid response format from AI endpoint"
                    logger.error(error_msg)
                    return AIResponse(success=False, content="", error_message=error_msg, status_code=response.status_code)
            else:
                error_msg = f"AI endpoint returned status {response.status_code}: {response.text}"
                logger.error(error_msg)
                return AIResponse(success=False, content="", error_message=error_msg, status_code=response.status_code)
                
        except requests.exceptions.Timeout:
            error_msg = f"Request timeout after {self.timeout} seconds"
            logger.error(error_msg)
            return AIResponse(success=False, content="", error_message=error_msg)
        
        except requests.exceptions.ConnectionError:
            error_msg = "Failed to connect to AI endpoint"
            logger.error(error_msg)
            return AIResponse(success=False, content="", error_message=error_msg)
        
        except requests.exceptions.RequestException as e:
            error_msg = f"Request failed: {str(e)}"
            logger.error(error_msg)
            return AIResponse(success=False, content="", error_message=error_msg)
        
        except (json.JSONDecodeError, ValueError):
            error_msg = "Failed to parse AI response as JSON"
            logger.error(error_msg)
            return AIResponse(success=False, content="", error_message=error_msg)
        
        except Exception as e:
            error_msg = f"Unexpected error during AI request: {str(e)}"
            logger.error(error_msg)
            return AIResponse(success=False, content="", error_message=error_msg)
    
    def is_available(self) -> bool:
        """Check if AI endpoint is available.
        
        Returns:
            True if endpoint is reachable, False otherwise
        """
        try:
            # Simple health check with minimal request
            payload = {
                "model": "gpt-4o-mini",
                "messages": [{"role": "user", "content": "test"}],
                "max_tokens": 1
            }
            
            response = self.session.post(
                f"{self.base_url}/chat/completions",
                json=payload,
                timeout=5  # Short timeout for health check
            )
            
            return response.status_code == 200
            
        except Exception:
            return False