"""
Supervisor agent for orchestrating multi-agent workflows.
Routes user requests to appropriate specialized agents based on intent classification.
"""

from typing import Optional, List

from agents.base_agent import BaseAgent
from core.state import WorkflowState, AgentType, MessageRole
from core.intent_classifier import IntentClassifier
from utils.llm_client import LLMMessage


class SupervisorAgent(BaseAgent):
    """Main orchestrator agent that routes requests to specialized agents."""
    
    def __init__(self):
        super().__init__(
            agent_type=AgentType.SUPERVISOR,
            name="Supervisor Agent",
            description="Orchestrates workflow and routes requests to specialized agents"
        )
        self.intent_classifier = IntentClassifier()
        self.available_agents = {}  # Will be populated by the graph builder
    
    def register_agent(self, agent: BaseAgent) -> None:
        """Register a specialized agent for routing."""
        self.available_agents[agent.agent_type] = agent
    
    def get_system_prompt(self) -> str:
        """Get the system prompt for the supervisor agent."""
        agent_descriptions = []
        for agent_type, agent in self.available_agents.items():
            capabilities = agent.get_capabilities()
            cap_list = "\n  - ".join(capabilities)
            agent_descriptions.append(f"- {agent.name}: {agent.description}\n  - {cap_list}")
        
        available_agents_text = "\n".join(agent_descriptions) if agent_descriptions else "No specialized agents available."
        
        return f"""You are a Supervisor Agent in a multi-agent system. Your role is to:

1. Analyze user requests and determine the best approach
2. Route requests to appropriate specialized agents when needed
3. Handle general conversation and coordination
4. Provide fallback assistance when specialized agents are unavailable

Available specialized agents:
{available_agents_text}

Guidelines:
- For complex requests, break them down and potentially use multiple agents
- Always be helpful and provide clear, actionable responses
- If you route to a specialist, explain why that agent is best suited
- Handle general conversation directly without routing
- Be transparent about your capabilities and limitations

Respond naturally and conversationally while being helpful and informative."""
    
    def process_request(self, state: WorkflowState) -> WorkflowState:
        """
        Process user request by classifying intent and routing appropriately.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated workflow state
        """
        try:
            # Classify the user's intent
            intent, confidence, reasoning, target_agent = self.intent_classifier.classify_intent(
                state.current_user_input,
                state.get_conversation_context()
            )
            
            # Update state with classification results
            state.detected_intent = intent
            state.intent_confidence = confidence
            
            # Record the routing decision
            state.add_handoff(
                from_agent=AgentType.SUPERVISOR,
                to_agent=target_agent,
                intent=intent,
                confidence=confidence,
                reasoning=reasoning
            )
            
            # Decide on routing strategy
            if self._should_route_to_specialist(state, target_agent, confidence):
                # Route to specialist agent
                state.current_agent = target_agent
                return self._route_to_specialist(state, target_agent)
            else:
                # Handle directly as supervisor
                return self._handle_directly(state)
                
        except Exception as e:
            return self.handle_error(state, e)
    
    def _should_route_to_specialist(self, state: WorkflowState, target_agent: AgentType, confidence: float) -> bool:
        """
        Determine if request should be routed to a specialist agent.
        
        Args:
            state: Current workflow state
            target_agent: Proposed target agent
            confidence: Classification confidence
            
        Returns:
            True if should route to specialist
        """
        # Don't route to self
        if target_agent == AgentType.SUPERVISOR:
            return False
        
        # Check if target agent is available
        if target_agent not in self.available_agents:
            return False
        
        # Route if confidence is high enough
        if confidence >= 0.7:
            return True
        
        # Route if in fallback mode and confidence is reasonable
        if state.fallback_mode and confidence >= 0.5:
            return True
        
        return False
    
    def _route_to_specialist(self, state: WorkflowState, target_agent: AgentType) -> WorkflowState:
        """
        Route the request to a specialist agent.
        
        Args:
            state: Current workflow state
            target_agent: Target agent type
            
        Returns:
            Updated workflow state
        """
        try:
            specialist = self.available_agents[target_agent]
            
            # Check if specialist can handle the request
            if not specialist.can_handle_request(state.current_user_input, state.detected_intent):
                return self._handle_directly(state)
            
            # Add routing message to conversation
            routing_message = f"I'll help you with that {state.detected_intent} request. Let me route this to our {specialist.name}."
            state.add_message(MessageRole.ASSISTANT, routing_message, AgentType.SUPERVISOR)
            
            # Process with specialist
            return specialist.process_request(state)
            
        except Exception as e:
            # Fallback to direct handling if routing fails
            state.record_error(f"Failed to route to {target_agent.value}: {str(e)}")
            return self._handle_directly(state)
    
    def _handle_directly(self, state: WorkflowState) -> WorkflowState:
        """
        Handle the request directly as supervisor.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated workflow state
        """
        try:
            # Build conversation for direct handling
            messages = self.build_conversation_messages(state)
            
            # Add context about available agents if relevant
            if state.detected_intent and state.intent_confidence > 0.3:
                context_msg = f"\n\nNote: This appears to be a {state.detected_intent} request (confidence: {state.intent_confidence:.2f}), but I'll handle it directly."
                messages[-1].content += context_msg
            
            # Generate response
            response = self.generate_response(messages, temperature=0.7)
            
            # Update state
            return self.update_state_with_response(state, response)
            
        except Exception as e:
            return self.handle_error(state, e)
    
    def get_capabilities(self) -> List[str]:
        """Get supervisor agent capabilities."""
        return [
            "General conversation and coordination",
            "Intent classification and agent routing",
            "Multi-agent workflow orchestration",
            "Fallback assistance for unclear requests",
            "Task breakdown and planning"
        ]
    
    def get_fallback_response(self, state: WorkflowState, error: Exception) -> str:
        """Generate fallback response for supervisor errors."""
        return (
            "I apologize, but I'm experiencing some technical difficulties. "
            "I'm working to resolve this issue. In the meantime, could you please "
            "rephrase your request or try asking something else?"
        )
    
    def get_routing_summary(self, state: WorkflowState) -> str:
        """
        Get a summary of routing decisions for debugging.
        
        Args:
            state: Current workflow state
            
        Returns:
            Routing summary string
        """
        if not state.handoff_history:
            return "No routing decisions made yet."
        
        summary_parts = ["Routing History:"]
        for handoff in state.handoff_history:
            summary_parts.append(
                f"- {handoff.from_agent.value} → {handoff.to_agent.value}: "
                f"{handoff.intent} (confidence: {handoff.confidence:.2f}) - {handoff.reasoning}"
            )
        
        return "\n".join(summary_parts)
