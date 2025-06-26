"""
Base agent class providing common functionality for all specialized agents.
Defines the interface and shared behavior for agent implementations.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from core.state import WorkflowState, AgentType, MessageRole
from core.tool_discovery import get_discovery_service, get_tool_registry, BaseTool
from utils.llm_client import get_default_llm_client, LLMMessage


class BaseAgent(ABC):
    """Abstract base class for all agents in the system."""
    
    def __init__(self, agent_type: AgentType, name: str, description: str):
        """
        Initialize the base agent.
        
        Args:
            agent_type: The type of agent for routing
            name: Human-readable name of the agent
            description: Description of agent capabilities
        """
        self.agent_type = agent_type
        self.name = name
        self.description = description
        self.llm_client = get_default_llm_client()
        
        # Tool discovery and management
        self.discovery_service = get_discovery_service()
        self.tool_registry = get_tool_registry()
        self.available_tools = self._discover_tools()
    
    def _discover_tools(self) -> List[BaseTool]:
        """Discover tools available to this agent."""
        return self.tool_registry.get_tools_for_agent(self.agent_type.value)
    
    def discover_tools_for_task(self, task_description: str) -> List[BaseTool]:
        """Discover relevant tools for a specific task."""
        return self.discovery_service.discover_tools_for_task(
            task_description, 
            self.agent_type.value
        )
    
    def execute_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """
        Execute a tool by name with given parameters.
        
        Args:
            tool_name: Name of the tool to execute
            **kwargs: Parameters to pass to the tool
            
        Returns:
            Tool execution result
        """
        tool = self.tool_registry.get_tool(tool_name)
        if not tool:
            return {"error": f"Tool '{tool_name}' not found"}
        
        if self.agent_type.value not in tool.metadata.agent_types:
            return {"error": f"Tool '{tool_name}' not available to {self.agent_type.value} agent"}
        
        try:
            return tool.execute(**kwargs)
        except Exception as e:
            return {"error": f"Tool execution failed: {str(e)}"}
    
    def get_tool_help(self, tool_name: str) -> str:
        """Get help text for a specific tool."""
        return self.discovery_service.get_tool_usage_suggestions(tool_name)
    
    def list_available_tools(self) -> List[Dict[str, Any]]:
        """Get a list of all tools available to this agent."""
        return [
            {
                "name": tool.metadata.name,
                "description": tool.metadata.description,
                "category": tool.metadata.category.value,
                "parameters": tool.metadata.parameters
            }
            for tool in self.available_tools
        ]
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """Get the system prompt that defines this agent's role and capabilities."""
        pass
    
    @abstractmethod
    def process_request(self, state: WorkflowState) -> WorkflowState:
        """
        Process a user request and update the workflow state.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated workflow state
        """
        pass
    
    def can_handle_request(self, user_input: str, intent: str) -> bool:
        """
        Determine if this agent can handle the given request.
        Override in subclasses for more sophisticated logic.
        
        Args:
            user_input: The user's input
            intent: The detected intent
            
        Returns:
            True if agent can handle the request
        """
        return True  # Base implementation accepts all requests
    
    def generate_response(self, messages: List[LLMMessage], **kwargs) -> str:
        """
        Generate a response using the LLM client.
        
        Args:
            messages: List of messages for the conversation
            **kwargs: Additional parameters for the LLM
            
        Returns:
            Generated response string
        """
        try:
            return self.llm_client.generate_response(messages, **kwargs)
        except Exception as e:
            return f"I apologize, but I encountered an error while processing your request: {str(e)}"
    
    def build_conversation_messages(self, state: WorkflowState, 
                                  include_system: bool = True) -> List[LLMMessage]:
        """
        Build conversation messages for LLM input.
        
        Args:
            state: Current workflow state
            include_system: Whether to include system prompt
            
        Returns:
            List of formatted messages
        """
        messages = []
        
        if include_system:
            messages.append(LLMMessage("system", self.get_system_prompt()))
        
        # Add conversation context
        context = state.get_conversation_context()
        if context:
            messages.append(LLMMessage("user", f"Previous conversation:\n{context}\n\nCurrent request: {state.current_user_input}"))
        else:
            messages.append(LLMMessage("user", state.current_user_input))
        
        return messages
    
    def update_state_with_response(self, state: WorkflowState, response: str) -> WorkflowState:
        """
        Update the workflow state with agent response.
        
        Args:
            state: Current workflow state
            response: Agent's response
            
        Returns:
            Updated workflow state
        """
        # Add agent response to message history
        state.add_message(MessageRole.ASSISTANT, response, self.agent_type)
        
        # Set as final response (can be overridden by supervisor)
        state.final_response = response
        
        # Store any intermediate results
        state.intermediate_results[f"{self.agent_type.value}_response"] = response
        
        return state
    
    def handle_error(self, state: WorkflowState, error: Exception) -> WorkflowState:
        """
        Handle errors gracefully and update state accordingly.
        
        Args:
            state: Current workflow state
            error: The exception that occurred
            
        Returns:
            Updated workflow state with error handling
        """
        error_message = f"Error in {self.name}: {str(error)}"
        state.record_error(error_message)
        
        # Generate fallback response
        fallback_response = self.get_fallback_response(state, error)
        state.add_message(MessageRole.ASSISTANT, fallback_response, self.agent_type)
        
        return state
    
    def get_fallback_response(self, state: WorkflowState, error: Exception) -> str:
        """
        Generate a fallback response when the agent encounters an error.
        
        Args:
            state: Current workflow state
            error: The exception that occurred
            
        Returns:
            Fallback response string
        """
        return (
            f"I apologize, but I'm currently unable to process your {self.agent_type.value} request. "
            f"Please try rephrasing your question or contact support if the issue persists."
        )
    
    def get_capabilities(self) -> List[str]:
        """
        Get a list of capabilities for this agent.
        Override in subclasses to provide specific capabilities.
        
        Returns:
            List of capability descriptions
        """
        capabilities = [f"General {self.agent_type.value} assistance"]
        
        # Add tool-based capabilities
        if self.available_tools:
            capabilities.append(f"Access to {len(self.available_tools)} specialized tools:")
            for tool in self.available_tools[:5]:  # Show first 5 tools
                capabilities.append(f"  • {tool.metadata.name}: {tool.metadata.description}")
            if len(self.available_tools) > 5:
                capabilities.append(f"  • ... and {len(self.available_tools) - 5} more tools")
        
        return capabilities
    
    def preprocess_request(self, state: WorkflowState) -> WorkflowState:
        """
        Preprocess the request before main processing.
        Override in subclasses for specialized preprocessing.
        
        Args:
            state: Current workflow state
            
        Returns:
            Preprocessed workflow state
        """
        return state
    
    def postprocess_response(self, state: WorkflowState, response: str) -> str:
        """
        Postprocess the response before returning.
        Override in subclasses for specialized postprocessing.
        
        Args:
            state: Current workflow state
            response: Generated response
            
        Returns:
            Postprocessed response
        """
        return response
    
    def __str__(self) -> str:
        """String representation of the agent."""
        return f"{self.name} ({self.agent_type.value}): {self.description}"
