"""
Configuration management for the LangGraph multi-agent system.
Uses Pydantic settings for type-safe configuration with environment variable support.
"""

import os
from typing import Optional, List
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # LLM Configuration
    openai_api_key: Optional[str] = Field(None, env="OPENAI_API_KEY")
    anthropic_api_key: Optional[str] = Field(None, env="ANTHROPIC_API_KEY")
    llm_provider: Optional[str] = Field(None, env="LLM_PROVIDER")  # openai, anthropic, cisco_openai
    default_model: str = Field("gpt-4o-mini", env="DEFAULT_MODEL")
    
    # Application Settings
    log_level: str = Field("INFO", env="LOG_LEVEL")
    max_retries: int = Field(3, env="MAX_RETRIES")
    timeout_seconds: int = Field(30, env="TIMEOUT_SECONDS")
    
    # Agent Configuration
    enable_research_agent: bool = Field(True, env="ENABLE_RESEARCH_AGENT")
    enable_code_agent: bool = Field(True, env="ENABLE_CODE_AGENT")
    enable_writing_agent: bool = Field(True, env="ENABLE_WRITING_AGENT")
    enable_data_agent: bool = Field(True, env="ENABLE_DATA_AGENT")
    
    # LLM Parameters
    temperature: float = Field(0.7, env="LLM_TEMPERATURE")
    max_tokens: int = Field(4096, env="LLM_MAX_TOKENS")
    
    # Demo Mode
    demo_mode: bool = Field(False, env="DEMO_MODE")
    
    # Workflow Settings
    enable_memory: bool = Field(True, env="ENABLE_MEMORY")
    enable_fallback: bool = Field(True, env="ENABLE_FALLBACK")
    intent_confidence_threshold: float = Field(0.7, env="INTENT_CONFIDENCE_THRESHOLD")
    
    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
    
    def get_enabled_agents(self) -> List[str]:
        """Get list of enabled agent types."""
        enabled = []
        if self.enable_research_agent:
            enabled.append("research")
        if self.enable_code_agent:
            enabled.append("code")
        if self.enable_writing_agent:
            enabled.append("writing")
        if self.enable_data_agent:
            enabled.append("data")
        return enabled
    
    def has_llm_provider(self) -> bool:
        """Check if at least one LLM provider is configured."""
        return bool(self.openai_api_key or self.anthropic_api_key)
    
    def get_llm_provider(self) -> Optional[str]:
        """Get the preferred LLM provider based on available keys."""
        if "gpt" in self.default_model.lower() and self.openai_api_key:
            return "openai"
        elif "claude" in self.default_model.lower() and self.anthropic_api_key:
            return "anthropic"
        elif self.openai_api_key:
            return "openai"
        elif self.anthropic_api_key:
            return "anthropic"
        else:
            return None
    
    def validate_configuration(self) -> List[str]:
        """
        Validate the configuration and return any issues.
        
        Returns:
            List of validation error messages
        """
        issues = []
        
        # Check LLM provider
        if not self.has_llm_provider():
            issues.append("No LLM API key provided (OPENAI_API_KEY or ANTHROPIC_API_KEY)")
        
        # Check agent configuration
        if not any([self.enable_research_agent, self.enable_code_agent, 
                   self.enable_writing_agent, self.enable_data_agent]):
            issues.append("At least one specialized agent must be enabled")
        
        # Check numeric ranges
        if self.max_retries < 0:
            issues.append("max_retries must be non-negative")
        
        if self.timeout_seconds <= 0:
            issues.append("timeout_seconds must be positive")
        
        if not 0.0 <= self.temperature <= 2.0:
            issues.append("temperature must be between 0.0 and 2.0")
        
        if self.max_tokens <= 0:
            issues.append("max_tokens must be positive")
        
        if not 0.0 <= self.intent_confidence_threshold <= 1.0:
            issues.append("intent_confidence_threshold must be between 0.0 and 1.0")
        
        return issues
    
    def to_dict(self) -> dict:
        """Convert settings to dictionary (excluding sensitive data)."""
        data = self.dict()
        
        # Mask sensitive information
        if data.get('openai_api_key'):
            data['openai_api_key'] = f"sk-...{data['openai_api_key'][-4:]}"
        if data.get('anthropic_api_key'):
            data['anthropic_api_key'] = f"sk-ant-...{data['anthropic_api_key'][-4:]}"
        
        return data


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get the global settings instance."""
    return settings


def reload_settings() -> Settings:
    """Reload settings from environment variables."""
    global settings
    settings = Settings()
    return settings


# Environment-specific configurations
def get_development_settings() -> Settings:
    """Get settings optimized for development."""
    dev_settings = Settings()
    dev_settings.log_level = "DEBUG"
    dev_settings.enable_memory = False  # Disable memory for easier debugging
    dev_settings.max_retries = 1  # Faster failure for development
    return dev_settings


def get_production_settings() -> Settings:
    """Get settings optimized for production."""
    prod_settings = Settings()
    prod_settings.log_level = "INFO"
    prod_settings.enable_memory = True
    prod_settings.max_retries = 3
    prod_settings.enable_fallback = True
    return prod_settings
