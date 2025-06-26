"""
Utility modules for the multi-agent system.
Contains LLM client abstractions and error handling utilities.
"""

from .llm_client import (
    get_default_llm_client,
    LLMMessage,
    CiscoOpenAIClient,
    create_llm_client
)
from .error_handler import (
    ErrorHandler,
    GracefulDegradation,
    ErrorSeverity,
    ErrorCategory,
    with_error_handling,
    safe_execute
)

__all__ = [
    'LLMClientFactory',
    'get_default_llm_client', 
    'LLMMessage',
    'LLMProvider',
    'BaseLLMClient',
    'ErrorHandler',
    'GracefulDegradation',
    'ErrorSeverity',
    'ErrorCategory',
    'with_error_handling',
    'safe_execute'
]
