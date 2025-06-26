"""
Error handling and graceful degradation utilities for the multi-agent system.
Provides comprehensive error recovery and fallback mechanisms.
"""

import logging
import traceback
from typing import Any, Callable, Dict, Optional, Tuple
from functools import wraps
from enum import Enum

from core.state import WorkflowState, AgentType, MessageRole


class ErrorSeverity(str, Enum):
    """Error severity levels for categorization."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(str, Enum):
    """Categories of errors in the system."""
    NETWORK = "network"
    API = "api"
    VALIDATION = "validation"
    PROCESSING = "processing"
    MEMORY = "memory"
    TIMEOUT = "timeout"
    UNKNOWN = "unknown"


class ErrorHandler:
    """Centralized error handling with graceful degradation strategies."""
    
    def __init__(self, max_retries: int = 3, enable_fallback: bool = True):
        """
        Initialize error handler.
        
        Args:
            max_retries: Maximum number of retry attempts
            enable_fallback: Whether to enable fallback mechanisms
        """
        self.max_retries = max_retries
        self.enable_fallback = enable_fallback
        self.error_history = []
        
        # Configure logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def classify_error(self, error: Exception) -> Tuple[ErrorCategory, ErrorSeverity]:
        """
        Classify an error by category and severity.
        
        Args:
            error: The exception to classify
            
        Returns:
            Tuple of (category, severity)
        """
        error_str = str(error).lower()
        error_type = type(error).__name__
        
        # Network-related errors
        if any(term in error_str for term in ['connection', 'network', 'timeout', 'unreachable']):
            return ErrorCategory.NETWORK, ErrorSeverity.MEDIUM
        
        # API-related errors
        if any(term in error_str for term in ['api', 'unauthorized', 'forbidden', 'rate limit']):
            return ErrorCategory.API, ErrorSeverity.HIGH
        
        # Validation errors
        if any(term in error_str for term in ['validation', 'invalid', 'missing', 'required']):
            return ErrorCategory.VALIDATION, ErrorSeverity.LOW
        
        # Memory/resource errors
        if any(term in error_str for term in ['memory', 'resource', 'limit exceeded']):
            return ErrorCategory.MEMORY, ErrorSeverity.HIGH
        
        # Processing errors
        if error_type in ['ValueError', 'TypeError', 'KeyError', 'AttributeError']:
            return ErrorCategory.PROCESSING, ErrorSeverity.MEDIUM
        
        # Timeout errors
        if 'timeout' in error_str or error_type == 'TimeoutError':
            return ErrorCategory.TIMEOUT, ErrorSeverity.MEDIUM
        
        # Unknown errors
        return ErrorCategory.UNKNOWN, ErrorSeverity.MEDIUM
    
    def handle_error(self, error: Exception, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Handle an error with appropriate recovery strategy.
        
        Args:
            error: The exception that occurred
            context: Additional context about the error
            
        Returns:
            Error handling result with recovery information
        """
        category, severity = self.classify_error(error)
        context = context or {}
        
        # Log the error
        self.logger.error(f"Error in {context.get('component', 'unknown')}: {str(error)}")
        self.logger.debug(f"Error details: {traceback.format_exc()}")
        
        # Record error in history
        error_record = {
            'error': str(error),
            'category': category,
            'severity': severity,
            'context': context,
            'timestamp': context.get('timestamp', 'unknown')
        }
        self.error_history.append(error_record)
        
        # Determine recovery strategy
        recovery_strategy = self._get_recovery_strategy(category, severity, context)
        
        return {
            'category': category,
            'severity': severity,
            'recovery_strategy': recovery_strategy,
            'can_retry': self._can_retry(category, context),
            'fallback_available': self._has_fallback(category, context),
            'user_message': self._get_user_friendly_message(category, severity)
        }
    
    def _get_recovery_strategy(self, category: ErrorCategory, severity: ErrorSeverity, 
                              context: Dict[str, Any]) -> str:
        """Determine the appropriate recovery strategy."""
        if severity == ErrorSeverity.CRITICAL:
            return "immediate_fallback"
        elif category == ErrorCategory.NETWORK:
            return "retry_with_backoff"
        elif category == ErrorCategory.API:
            return "check_credentials_and_retry"
        elif category == ErrorCategory.VALIDATION:
            return "request_clarification"
        elif category == ErrorCategory.TIMEOUT:
            return "retry_with_longer_timeout"
        else:
            return "graceful_degradation"
    
    def _can_retry(self, category: ErrorCategory, context: Dict[str, Any]) -> bool:
        """Determine if the operation can be retried."""
        retry_count = context.get('retry_count', 0)
        
        if retry_count >= self.max_retries:
            return False
        
        # Don't retry validation errors
        if category == ErrorCategory.VALIDATION:
            return False
        
        return True
    
    def _has_fallback(self, category: ErrorCategory, context: Dict[str, Any]) -> bool:
        """Check if fallback mechanism is available."""
        if not self.enable_fallback:
            return False
        
        # Fallback available for most categories except critical validation
        return category != ErrorCategory.VALIDATION
    
    def _get_user_friendly_message(self, category: ErrorCategory, severity: ErrorSeverity) -> str:
        """Generate user-friendly error message."""
        base_messages = {
            ErrorCategory.NETWORK: "I'm having trouble connecting to external services. Please check your internet connection and try again.",
            ErrorCategory.API: "I'm experiencing issues with external services. This might be temporary - please try again in a few moments.",
            ErrorCategory.VALIDATION: "I need more information to process your request properly. Could you provide additional details?",
            ErrorCategory.PROCESSING: "I encountered an issue while processing your request. Let me try a different approach.",
            ErrorCategory.MEMORY: "I'm running low on resources. Please try breaking your request into smaller parts.",
            ErrorCategory.TIMEOUT: "Your request is taking longer than expected. Let me try with a simplified approach.",
            ErrorCategory.UNKNOWN: "I encountered an unexpected issue. Let me try to help you in a different way."
        }
        
        message = base_messages.get(category, "I encountered a technical issue.")
        
        if severity == ErrorSeverity.CRITICAL:
            message += " I'm switching to a simpler mode to continue helping you."
        
        return message


def with_error_handling(error_handler: ErrorHandler = None, 
                       component_name: str = "unknown",
                       fallback_response: str = None):
    """
    Decorator for adding error handling to functions.
    
    Args:
        error_handler: ErrorHandler instance to use
        component_name: Name of the component for logging
        fallback_response: Default response on error
    """
    if error_handler is None:
        error_handler = ErrorHandler()
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                context = {
                    'component': component_name,
                    'function': func.__name__,
                    'args_count': len(args),
                    'kwargs_keys': list(kwargs.keys())
                }
                
                error_info = error_handler.handle_error(e, context)
                
                # Return fallback response or re-raise based on severity
                if error_info['severity'] == ErrorSeverity.CRITICAL:
                    if fallback_response:
                        return fallback_response
                    else:
                        raise
                else:
                    raise
        
        return wrapper
    return decorator


class GracefulDegradation:
    """Implements graceful degradation strategies for the multi-agent system."""
    
    def __init__(self, error_handler: ErrorHandler = None):
        """Initialize graceful degradation with error handler."""
        self.error_handler = error_handler or ErrorHandler()
        self.degradation_levels = {
            'full': 'All agents available with full capabilities',
            'limited': 'Limited agent capabilities due to resource constraints',
            'basic': 'Basic functionality only - supervisor agent responses',
            'minimal': 'Minimal responses with error acknowledgment'
        }
        self.current_level = 'full'
    
    def determine_degradation_level(self, state: WorkflowState) -> str:
        """
        Determine appropriate degradation level based on error history.
        
        Args:
            state: Current workflow state
            
        Returns:
            Degradation level identifier
        """
        error_count = state.error_count
        
        if error_count == 0:
            return 'full'
        elif error_count <= 2:
            return 'limited'
        elif error_count <= 5:
            return 'basic'
        else:
            return 'minimal'
    
    def apply_degradation(self, state: WorkflowState, target_level: str = None) -> WorkflowState:
        """
        Apply degradation strategy to the workflow state.
        
        Args:
            state: Current workflow state
            target_level: Target degradation level (auto-determined if None)
            
        Returns:
            Modified workflow state
        """
        if target_level is None:
            target_level = self.determine_degradation_level(state)
        
        self.current_level = target_level
        
        if target_level == 'limited':
            # Reduce agent capabilities but keep routing
            state.fallback_mode = True
            
        elif target_level == 'basic':
            # Force routing to supervisor only
            state.current_agent = AgentType.SUPERVISOR
            state.fallback_mode = True
            
        elif target_level == 'minimal':
            # Minimal response mode
            state.should_continue = False
            state.final_response = self._get_minimal_response(state)
        
        return state
    
    def _get_minimal_response(self, state: WorkflowState) -> str:
        """Generate minimal response for severe degradation."""
        return (
            "I apologize, but I'm currently experiencing technical difficulties "
            "that prevent me from providing a complete response. Please try:\n"
            "1. Simplifying your request\n"
            "2. Trying again in a few minutes\n"
            "3. Contacting support if the issue persists\n\n"
            "Thank you for your patience."
        )
    
    def get_degradation_status(self) -> Dict[str, Any]:
        """Get current degradation status information."""
        return {
            'current_level': self.current_level,
            'description': self.degradation_levels[self.current_level],
            'available_levels': list(self.degradation_levels.keys()),
            'error_count': len(self.error_handler.error_history)
        }


# Global error handler instance
default_error_handler = ErrorHandler()


def safe_execute(func: Callable, *args, fallback_result: Any = None, **kwargs) -> Tuple[Any, Optional[Exception]]:
    """
    Safely execute a function with error handling.
    
    Args:
        func: Function to execute
        *args: Function arguments
        fallback_result: Result to return on error
        **kwargs: Function keyword arguments
        
    Returns:
        Tuple of (result, error) where error is None on success
    """
    try:
        result = func(*args, **kwargs)
        return result, None
    except Exception as e:
        default_error_handler.handle_error(e, {'function': func.__name__})
        return fallback_result, e
