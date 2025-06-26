"""
LLM client implementation for Cisco Enterprise OpenAI integration.
Provides a unified interface for the multi-agent system.
"""

import os
import json
import time
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

try:
    from openai import AzureOpenAI
    import requests
except ImportError:
    AzureOpenAI = None
    requests = None


@dataclass
class LLMMessage:
    """Represents a message in the conversation."""
    role: str
    content: str
    
    def to_openai_format(self) -> Dict[str, str]:
        """Convert to OpenAI message format."""
        return {"role": self.role, "content": self.content}


class CiscoOpenAIClient:
    """Cisco Enterprise OpenAI client using AzureOpenAI with OAuth."""
    
    def __init__(self):
        """Initialize Cisco OpenAI client."""
        self.config = self._load_config()
        self.client = None
        self._access_token = None
        self._token_expires_at = 0
        if self.is_available():
            self._initialize_client()
    
    def _load_config(self) -> Dict[str, str]:
        """Load configuration from environment variables or config file."""
        config = {}
        
        # Load from environment variables first
        env_mapping = {
            'CISCO_OPENAI_ENDPOINT': 'azure_endpoint',
            'CISCO_OPENAI_API_VERSION': 'api_version',
            'CISCO_OPENAI_CLIENT_ID': 'client_id',
            'CISCO_OPENAI_CLIENT_SECRET': 'client_secret',
            'CISCO_OPENAI_TOKEN_URL': 'token_url',
            'CISCO_OPENAI_APPKEY': 'app_key'
        }
        
        for env_var, config_key in env_mapping.items():
            if os.getenv(env_var):
                config[config_key] = os.getenv(env_var)
        
        # Try to load from config file if environment variables not set
        if not config:
            config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'openai.properties')
            if os.path.exists(config_path):
                try:
                    from utils.secret_util import collect_property_file_contents
                    config = collect_property_file_contents("openai", config_path)
                except Exception:
                    pass
        
        return config
    
    def _get_fresh_oauth_token(self) -> Optional[str]:
        """Get a cached OAuth token or fetch a new one if expired."""
        
        # Check if we have a valid cached token
        current_time = time.time()
        if (self._access_token and 
            self._token_expires_at > current_time + 300):  # 5 minutes buffer
            return self._access_token
        
        # Need to get a new token
        if not all(key in self.config for key in ['client_id', 'client_secret', 'token_url']):
            return None
        try:
            if not requests:
                raise ImportError("requests library not available")
            
            data = {
                'grant_type': 'client_credentials',
                'client_id': self.config['client_id'],
                'client_secret': self.config['client_secret']
            }
            
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'application/json'
            }
            
            response = requests.post(self.config['token_url'], data=data, headers=headers)
            response.raise_for_status()
            
            token_data = response.json()
            token = token_data.get('access_token')
            expires_in = token_data.get('expires_in', 3600)  # Default 1 hour
            
            if token:
                print(f"✅ Successfully obtained OAuth token (length: {len(token)})")
                # Cache the token with expiry
                self._access_token = token
                self._token_expires_at = current_time + expires_in
            
            return token
            
        except Exception as e:
            print(f"❌ Failed to get OAuth token: {e}")
            return None
    
    def _initialize_client(self):
        """Initialize the Azure OpenAI client with Cisco configuration."""
        if not AzureOpenAI:
            raise ImportError("openai package not installed. Run: pip install openai")
        
        try:
            # Don't initialize with token here - we'll get fresh token per request
            # Just set up the basic client configuration
            self.client = "configured"  # Placeholder to indicate setup is done
            
        except Exception as e:
            print(f"Failed to initialize Cisco OpenAI client: {e}")
            self.client = None
    
    def _get_fresh_client(self):
        """Get a client with a cached or fresh token."""
        if not AzureOpenAI:
            raise ImportError("openai package not installed. Run: pip install openai")
        
        # Get cached or fresh OAuth token
        token = self._get_fresh_oauth_token()
        if not token:
            raise ValueError("Could not obtain OAuth token")
        
        # Return client with token in Authorization header (standard OAuth)
        return AzureOpenAI(
            api_key=token,  # Pass token as API key
            api_version=self.config.get("api_version", "2024-07-01-preview"),
            azure_endpoint=self.config.get("azure_endpoint", ""),
            default_headers={
                "Authorization": f"Bearer {token}",
                "X-OAuth-Token": token,  # Alternative header name
                "oauthtoken": token     # Cisco-specific header
            }
        )
    
    def is_available(self) -> bool:
        """Check if Cisco OpenAI is properly configured."""
        required_keys = ['azure_endpoint', 'client_id', 'client_secret', 'token_url', 'app_key']
        return (
            AzureOpenAI is not None and 
            requests is not None and
            all(key in self.config for key in required_keys)
        )
    
    def generate_response(self, messages: List[LLMMessage], **kwargs) -> str:
        """Generate response using Cisco Enterprise OpenAI."""
        try:
            # Get a fresh client with current token for each request
            # This ensures we always have a valid token
            client = self._get_fresh_client()
            
            # Convert messages to OpenAI format
            openai_messages = [msg.to_openai_format() for msg in messages]
            
            # Get appkey for the user parameter
            appkey = self.config.get('app_key', 'cisco-multi-agent-system')
            
            # Make API call with fresh client using Cisco's required format
            response = client.chat.completions.create(
                model=kwargs.get('model', 'gpt-4o-mini'),  # Use gpt-4o-mini as shown in example
                messages=openai_messages,
                user=f'{{"appkey": "{appkey}"}}'  # Cisco-specific user format with appkey
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Error generating response: {str(e)}"
    
    def test_connection(self) -> Dict[str, Any]:
        """Test the connection to Cisco OpenAI with detailed error information."""
        try:
            if not self.is_available():
                return {
                    "success": False,
                    "error": "Cisco OpenAI not properly configured",
                    "config_status": {
                        "has_azure_endpoint": "azure_endpoint" in self.config,
                        "has_client_id": "client_id" in self.config,
                        "has_client_secret": "client_secret" in self.config,
                        "has_token_url": "token_url" in self.config,
                        "azure_openai_available": AzureOpenAI is not None,
                        "requests_available": requests is not None
                    }
                }
            
            # Test with a simple message (this will handle token acquisition internally)
            test_messages = [LLMMessage("user", "Say 'Hello from Cisco OpenAI!' in exactly those words.")]
            response = self.generate_response(test_messages, max_tokens=50)
            
            if response.startswith("Error"):
                return {
                    "success": False,
                    "error": response,
                    "endpoint": self.config.get("azure_endpoint", "Not configured"),
                    "token_acquired": True
                }
            
            return {
                "success": True,
                "response": response,
                "model": "gpt-4",
                "endpoint": self.config.get("azure_endpoint", "Not configured"),
                "token_acquired": True
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "config_status": self.config
            }


# Global singleton instance
_cisco_client_instance = None


def get_default_llm_client() -> CiscoOpenAIClient:
    """Get the default LLM client (Cisco OpenAI) - singleton instance."""
    global _cisco_client_instance
    if _cisco_client_instance is None:
        _cisco_client_instance = CiscoOpenAIClient()
    return _cisco_client_instance


def create_llm_client(**kwargs) -> CiscoOpenAIClient:
    """Create a new Cisco OpenAI client instance."""
    return CiscoOpenAIClient()
