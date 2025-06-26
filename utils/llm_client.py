"""
LLM client abstraction for supporting multiple LLM providers.
Provides a unified interface for OpenAI, Anthropic, and other providers.
"""

import os
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from enum import Enum

# Note: Import errors will resolve after installing dependencies
try:
    from openai import OpenAI, AzureOpenAI
    from anthropic import Anthropic
    import requests
except ImportError:
    # Will be resolved after pip install
    OpenAI = None
    AzureOpenAI = None
    Anthropic = None
    requests = None


class LLMProvider(str, Enum):
    """Supported LLM providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    CISCO_OPENAI = "cisco_openai"  # Cisco Enterprise OpenAI


class LLMMessage:
    """Standardized message format across providers."""
    
    def __init__(self, role: str, content: str):
        self.role = role
        self.content = content
    
    def to_openai_format(self) -> Dict[str, str]:
        """Convert to OpenAI message format."""
        return {"role": self.role, "content": self.content}
    
    def to_anthropic_format(self) -> Dict[str, str]:
        """Convert to Anthropic message format."""
        return {"role": self.role, "content": self.content}


class BaseLLMClient(ABC):
    """Abstract base class for LLM clients."""
    
    def __init__(self, model: str, temperature: float = 0.7):
        self.model = model
        self.temperature = temperature
    
    @abstractmethod
    def generate_response(self, messages: List[LLMMessage], **kwargs) -> str:
        """Generate a response from the LLM."""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the client is properly configured and available."""
        pass


class OpenAIClient(BaseLLMClient):
    """OpenAI client implementation."""
    
    def __init__(self, model: str = "gpt-4o-mini", temperature: float = 0.7):
        super().__init__(model, temperature)
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        if OpenAI is None:
            raise ImportError("openai package not installed. Run: pip install openai")
        
        self.client = OpenAI(api_key=api_key)
    
    def generate_response(self, messages: List[LLMMessage], **kwargs) -> str:
        """Generate response using OpenAI API."""
        try:
            openai_messages = [msg.to_openai_format() for msg in messages]
            
            # Remove temperature from kwargs if present to avoid conflicts
            kwargs.pop('temperature', None)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=openai_messages,
                temperature=self.temperature,
                **kwargs
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            raise RuntimeError(f"OpenAI API error: {str(e)}")
    
    def is_available(self) -> bool:
        """Check if OpenAI client is available."""
        try:
            return bool(os.getenv("OPENAI_API_KEY")) and OpenAI is not None
        except:
            return False


class AnthropicClient(BaseLLMClient):
    """Anthropic client implementation."""
    
    def __init__(self, model: str = "claude-3-5-sonnet-20241022", temperature: float = 0.7):
        super().__init__(model, temperature)
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is required")
        
        if Anthropic is None:
            raise ImportError("anthropic package not installed. Run: pip install anthropic")
        
        self.client = Anthropic(api_key=api_key)
    
    def generate_response(self, messages: List[LLMMessage], **kwargs) -> str:
        """Generate response using Anthropic API."""
        try:
            # Anthropic requires system messages to be separate
            system_messages = [msg for msg in messages if msg.role == "system"]
            user_messages = [msg for msg in messages if msg.role != "system"]
            
            system_content = "\n".join([msg.content for msg in system_messages])
            anthropic_messages = [msg.to_anthropic_format() for msg in user_messages]
            
            # Remove conflicting parameters from kwargs
            kwargs.pop('temperature', None)
            kwargs.pop('max_tokens', None)
            
            response = self.client.messages.create(
                model=self.model,
                messages=anthropic_messages,
                system=system_content if system_content else None,
                temperature=self.temperature,
                max_tokens=4096,
                **kwargs
            )
            
            return response.content[0].text
        
        except Exception as e:
            raise RuntimeError(f"Anthropic API error: {str(e)}")
    
    def is_available(self) -> bool:
        """Check if Anthropic client is available."""
        try:
            return bool(os.getenv("ANTHROPIC_API_KEY")) and Anthropic is not None
        except:
            return False


class DemoLLMClient(BaseLLMClient):
    """Demo LLM client that provides mock responses for testing."""
    
    def __init__(self, model: str = "demo-model", temperature: float = 0.7):
        super().__init__(model, temperature)
        self.response_templates = {
            "research": "Based on my research, I can provide information about {}. This is a demo response from the research agent.",
            "code": "Here's a code solution for your request: ```python\n# Demo code for {}\nprint('Hello from the code agent!')\n```",
            "writing": "I can help you write content about {}. This is a demo response from the writing agent with structured, clear content.",
            "data": "I can analyze data related to {}. This is a demo response from the data agent showing analytical insights.",
            "default": "Hello! I'm the supervisor agent in demo mode. I would normally route your request about '{}' to the appropriate specialist agent. This is a demo response showing the system is working."
        }
    
    def generate_response(self, messages: List[LLMMessage], **kwargs) -> str:
        """Generate a demo response based on the message content."""
        try:
            # Get the last user message
            user_messages = [msg for msg in messages if msg.role == "user"]
            if not user_messages:
                return "Demo response: No user message found."
            
            content = user_messages[-1].content.lower()
            
            # Simple intent detection for demo
            if any(word in content for word in ["research", "find", "search", "information"]):
                agent_type = "research"
            elif any(word in content for word in ["code", "program", "function", "script"]):
                agent_type = "code"
            elif any(word in content for word in ["write", "content", "article", "document"]):
                agent_type = "writing"
            elif any(word in content for word in ["data", "analyze", "chart", "statistics"]):
                agent_type = "data"
            else:
                agent_type = "default"
            
            # Extract key terms for personalized response
            key_terms = " ".join([word for word in content.split() if len(word) > 3])[:50]
            if not key_terms:
                key_terms = "your request"
            
            return self.response_templates[agent_type].format(key_terms)
            
        except Exception as e:
            return f"Demo response: Error generating demo response: {str(e)}"
    
    def is_available(self) -> bool:
        """Demo client is always available."""
        return True


class CiscoOpenAIClient(BaseLLMClient):
    """Cisco Enterprise OpenAI client implementation using Azure OpenAI with OAuth."""
    
    def __init__(self, model: str = "gpt-4o-mini", temperature: float = 0.7):
        super().__init__(model, temperature)
        
        if AzureOpenAI is None or requests is None:
            raise ImportError("Required packages not installed. Run: pip install openai requests")
        
        # Import here to avoid circular imports
        from utils.secret_util import collect_property_file_contents, collect_property_file_contents_env
        
        # Try to load config from file first, then environment variables
        try:
            config = collect_property_file_contents('openai')
        except (FileNotFoundError, ValueError):
            # Fall back to environment variables
            config = collect_property_file_contents_env('cisco_openai')
            if not config:
                raise ValueError(
                    "Cisco OpenAI configuration not found. "
                    "Create config/openai.properties or set CISCO_OPENAI_* environment variables"
                )
        
        self.token_url = config.get('token_url')
        self.client_id = config.get('client_id')
        self.client_secret = config.get('client_secret')
        self.grant_type = config.get('grant_type', 'client_credentials')
        self.app_key = config.get('app_key')
        self.azure_endpoint = config.get('azure_endpoint', 'https://chat-ai.cisco.com')
        self.api_version = config.get('api_version', '2024-07-01-preview')
        
        # Override model if specified in config
        if 'model' in config:
            self.model = config['model']
        
        # Validate required config
        required_fields = ['token_url', 'client_id', 'client_secret', 'app_key']
        missing_fields = [field for field in required_fields if not config.get(field)]
        if missing_fields:
            raise ValueError(f"Missing required configuration fields: {missing_fields}")
        
        # Initialize client (will get token on first use)
        self.client = None
        self._token = None
        self._token_expires_at = 0
    
    def _get_openai_token(self) -> str:
        """Get OAuth token for Cisco OpenAI API."""
        import time
        
        # Check if we have a valid token
        if self._token and time.time() < self._token_expires_at:
            return self._token
        
        payload = {
            "grant_type": self.grant_type,
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        
        try:
            response = requests.post(self.token_url, data=payload)
            
            if response.status_code == 200:
                token_info = response.json()
                self._token = token_info.get("access_token")
                
                # Set expiration time (assume 1 hour if not provided)
                expires_in = token_info.get("expires_in", 3600)
                self._token_expires_at = time.time() + expires_in - 60  # 1 minute buffer
                
                return self._token
            else:
                raise RuntimeError(f"Token request failed: {response.status_code} {response.text}")
                
        except Exception as e:
            raise RuntimeError(f"Failed to obtain OAuth token: {str(e)}")
    
    def _ensure_client(self):
        """Ensure the Azure OpenAI client is initialized with a valid token."""
        if not self.client or not self._token:
            token = self._get_openai_token()
            self.client = AzureOpenAI(
                azure_endpoint=self.azure_endpoint,
                api_key=token,
                api_version=self.api_version
            )
    
    def generate_response(self, messages: List[LLMMessage], **kwargs) -> str:
        """Generate response using Cisco Enterprise OpenAI API."""
        try:
            self._ensure_client()
            
            openai_messages = [msg.to_openai_format() for msg in messages]
            
            # Remove conflicting parameters from kwargs
            kwargs.pop('temperature', None)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=openai_messages,
                temperature=self.temperature,
                user=f'{{"appkey": "{self.app_key}"}}',
                **kwargs
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            # Try to refresh token if it's an auth error
            if "401" in str(e) or "403" in str(e) or "unauthorized" in str(e).lower():
                self._token = None  # Force token refresh
                try:
                    self._ensure_client()
                    response = self.client.chat.completions.create(
                        model=self.model,
                        messages=openai_messages,
                        temperature=self.temperature,
                        user=f'{{"appkey": "{self.app_key}"}}',
                        **kwargs
                    )
                    return response.choices[0].message.content
                except Exception as retry_e:
                    raise RuntimeError(f"Cisco OpenAI API error (after retry): {str(retry_e)}")
            else:
                raise RuntimeError(f"Cisco OpenAI API error: {str(e)}")
    
    def is_available(self) -> bool:
        """Check if Cisco OpenAI client is available."""
        try:
            # Check if we can get a token
            token = self._get_openai_token()
            return bool(token)
        except:
            return False


class LLMClientFactory:
    """Factory for creating LLM clients based on configuration."""
    
    @staticmethod
    def create_client(provider: Optional[LLMProvider] = None, 
                     model: Optional[str] = None) -> BaseLLMClient:
        """Create an LLM client based on provider preference and availability."""
        
        # Check for demo mode
        if os.getenv("DEMO_MODE", "").lower() in ["true", "1", "yes"]:
            return DemoLLMClient()
        
        # Use provided model or fall back to environment variable
        if model is None:
            model = os.getenv("DEFAULT_MODEL", "gpt-4o-mini")
        
        # Auto-detect provider if not specified
        if provider is None:
            # Check for explicit provider preference in environment
            env_provider = os.getenv("LLM_PROVIDER", "").lower()
            if env_provider == "cisco_openai":
                provider = LLMProvider.CISCO_OPENAI
            elif env_provider == "openai":
                provider = LLMProvider.OPENAI
            elif env_provider == "anthropic":
                provider = LLMProvider.ANTHROPIC
            elif "gpt" in model.lower() or "openai" in model.lower():
                # Try Cisco OpenAI first for GPT models
                try:
                    cisco_client = CiscoOpenAIClient(model)
                    if cisco_client.is_available():
                        provider = LLMProvider.CISCO_OPENAI
                    else:
                        provider = LLMProvider.OPENAI
                except:
                    provider = LLMProvider.OPENAI
            elif "claude" in model.lower() or "anthropic" in model.lower():
                provider = LLMProvider.ANTHROPIC
            else:
                # Default preference order: Cisco OpenAI -> OpenAI -> Anthropic
                try:
                    cisco_client = CiscoOpenAIClient(model="gpt-4o-mini")
                    if cisco_client.is_available():
                        provider = LLMProvider.CISCO_OPENAI
                    elif OpenAIClient(model="gpt-4o-mini").is_available():
                        provider = LLMProvider.OPENAI
                    elif AnthropicClient(model="claude-3-5-sonnet-20241022").is_available():
                        provider = LLMProvider.ANTHROPIC
                    else:
                        raise RuntimeError("No LLM provider is available. Check API keys.")
                except Exception as e:
                    if "OpenAI" in str(e):
                        try:
                            if AnthropicClient(model="claude-3-5-sonnet-20241022").is_available():
                                provider = LLMProvider.ANTHROPIC
                            else:
                                raise RuntimeError("No LLM provider is available. Check API keys.")
                        except:
                            raise RuntimeError("No LLM provider is available. Check API keys.")
                    else:
                        raise RuntimeError("No LLM provider is available. Check API keys.")
        
        # Create the appropriate client
        if provider == LLMProvider.OPENAI:
            return OpenAIClient(model)
        elif provider == LLMProvider.ANTHROPIC:
            return AnthropicClient(model)
        elif provider == LLMProvider.CISCO_OPENAI:
            return CiscoOpenAIClient(model)
        else:
            raise ValueError(f"Unsupported provider: {provider}")


def get_default_llm_client() -> BaseLLMClient:
    """Get the default LLM client based on environment configuration."""
    return LLMClientFactory.create_client()
