"""
Centralized state management for LangGraph multi-agent orchestration.
Handles conversation history, agent metadata, and workflow state.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class AgentType(str, Enum):
    """Available agent types in the system."""
    SUPERVISOR = "supervisor"
    RESEARCH = "research"
    CODE = "code"
    WRITING = "writing"
    DATA = "data"


class MessageRole(str, Enum):
    """Message roles in conversation."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class Message(BaseModel):
    """Individual message in conversation history."""
    role: MessageRole
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)
    agent_type: Optional[AgentType] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AgentHandoff(BaseModel):
    """Information about agent handoffs and routing decisions."""
    from_agent: AgentType
    to_agent: AgentType
    intent: str
    confidence: float
    reasoning: str
    timestamp: datetime = Field(default_factory=datetime.now)


class WorkflowState(BaseModel):
    """Central state object for the LangGraph workflow."""
    
    # Conversation context
    messages: List[Message] = Field(default_factory=list)
    current_user_input: str = ""
    
    # Agent routing
    current_agent: AgentType = AgentType.SUPERVISOR
    detected_intent: Optional[str] = None
    intent_confidence: float = 0.0
    
    # Handoff tracking
    handoff_history: List[AgentHandoff] = Field(default_factory=list)
    
    # Error handling
    error_count: int = 0
    last_error: Optional[str] = None
    fallback_mode: bool = False
    
    # Task context
    task_context: Dict[str, Any] = Field(default_factory=dict)
    intermediate_results: Dict[str, Any] = Field(default_factory=dict)
    
    # Workflow control
    should_continue: bool = True
    final_response: Optional[str] = None
    
    def add_message(self, role: MessageRole, content: str, agent_type: Optional[AgentType] = None) -> None:
        """Add a new message to the conversation history."""
        message = Message(
            role=role,
            content=content,
            agent_type=agent_type
        )
        self.messages.append(message)
    
    def add_handoff(self, from_agent: AgentType, to_agent: AgentType, 
                   intent: str, confidence: float, reasoning: str) -> None:
        """Record an agent handoff for tracking and debugging."""
        handoff = AgentHandoff(
            from_agent=from_agent,
            to_agent=to_agent,
            intent=intent,
            confidence=confidence,
            reasoning=reasoning
        )
        self.handoff_history.append(handoff)
    
    def record_error(self, error_message: str) -> None:
        """Record an error and increment error count."""
        self.error_count += 1
        self.last_error = error_message
        
        # Enable fallback mode after multiple errors
        if self.error_count >= 3:
            self.fallback_mode = True
    
    def get_conversation_context(self, max_messages: int = 10) -> str:
        """Get formatted conversation context for agent prompts."""
        recent_messages = self.messages[-max_messages:] if self.messages else []
        
        context_parts = []
        for msg in recent_messages:
            role_str = msg.role.value.upper()
            agent_str = f"[{msg.agent_type.value}]" if msg.agent_type else ""
            context_parts.append(f"{role_str}{agent_str}: {msg.content}")
        
        return "\n".join(context_parts)
    
    def reset_for_new_input(self, user_input: str) -> None:
        """Reset state for processing new user input."""
        self.current_user_input = user_input
        self.current_agent = AgentType.SUPERVISOR
        self.detected_intent = None
        self.intent_confidence = 0.0
        self.should_continue = True
        self.final_response = None
        self.task_context.clear()
        self.intermediate_results.clear()
