"""
LLM-based intent classification for routing user requests to appropriate agents.
Uses structured prompting to identify user intent with confidence scoring.
"""

from typing import Dict, List, Tuple
from enum import Enum

from utils.llm_client import get_default_llm_client, LLMMessage
from core.state import AgentType


class IntentCategory(str, Enum):
    """Predefined intent categories mapped to agent types."""
    RESEARCH = "research"
    CODING = "coding"
    WRITING = "writing"
    DATA_ANALYSIS = "data_analysis"
    GENERAL = "general"


class IntentClassifier:
    """LLM-powered intent classifier for agent routing."""
    
    # Intent to agent mapping
    INTENT_AGENT_MAP = {
        IntentCategory.RESEARCH: AgentType.RESEARCH,
        IntentCategory.CODING: AgentType.CODE,
        IntentCategory.WRITING: AgentType.WRITING,
        IntentCategory.DATA_ANALYSIS: AgentType.DATA,
        IntentCategory.GENERAL: AgentType.SUPERVISOR,  # Fallback to supervisor
    }
    
    def __init__(self):
        self.llm_client = get_default_llm_client()
        self.classification_prompt = self._build_classification_prompt()
    
    def _build_classification_prompt(self) -> str:
        """Build the system prompt for intent classification."""
        return """You are an expert intent classifier for a multi-agent system. Your job is to analyze user input and determine which specialized agent should handle the request.

Available intent categories:
- RESEARCH: Information gathering, web search, fact-checking, literature review, knowledge retrieval
- CODING: Programming tasks, debugging, code review, technical implementation, software development
- WRITING: Content creation, editing, documentation, creative writing, communication
- DATA_ANALYSIS: Data processing, statistics, visualization, analysis, reporting
- GENERAL: Conversations, greetings, unclear requests, or requests that don't fit other categories

Instructions:
1. Analyze the user's input carefully
2. Consider the primary intent and task type
3. Choose the most appropriate category
4. Provide a confidence score (0.0 to 1.0)
5. Give a brief reasoning for your decision

Respond in this exact JSON format:
{
    "intent": "CATEGORY_NAME",
    "confidence": 0.85,
    "reasoning": "Brief explanation of why this category was chosen"
}

Be decisive but honest about uncertainty. Use GENERAL for ambiguous cases."""
    
    def classify_intent(self, user_input: str, conversation_context: str = "") -> Tuple[str, float, str, AgentType]:
        """
        Classify user intent and return routing information.
        
        Args:
            user_input: The current user input to classify
            conversation_context: Previous conversation for context
            
        Returns:
            Tuple of (intent, confidence, reasoning, agent_type)
        """
        try:
            # Build the classification prompt
            messages = [
                LLMMessage("system", self.classification_prompt),
                LLMMessage("user", self._format_classification_request(user_input, conversation_context))
            ]
            
            # Get LLM response
            response = self.llm_client.generate_response(messages, temperature=0.3)
            
            # Parse the JSON response
            result = self._parse_classification_response(response)
            
            # Map intent to agent type
            intent = result["intent"]
            confidence = result["confidence"]
            reasoning = result["reasoning"]
            
            # Get agent type from mapping
            try:
                intent_category = IntentCategory(intent.lower())
                agent_type = self.INTENT_AGENT_MAP[intent_category]
            except ValueError:
                # Fallback for unknown intents
                agent_type = AgentType.SUPERVISOR
                confidence = max(0.1, confidence * 0.5)  # Reduce confidence for unknown intents
                reasoning += " (Unknown intent, routing to supervisor)"
            
            return intent, confidence, reasoning, agent_type
            
        except Exception as e:
            # Fallback on any error
            return (
                IntentCategory.GENERAL.value,
                0.1,
                f"Classification failed: {str(e)}. Using fallback.",
                AgentType.SUPERVISOR
            )
    
    def _format_classification_request(self, user_input: str, conversation_context: str) -> str:
        """Format the user input for intent classification."""
        request_parts = [
            "Please classify the following user input:",
            f"User Input: {user_input}"
        ]
        
        if conversation_context.strip():
            request_parts.extend([
                "",
                "Conversation Context:",
                conversation_context
            ])
        
        return "\n".join(request_parts)
    
    def _parse_classification_response(self, response: str) -> Dict:
        """Parse the LLM response to extract classification results."""
        import json
        
        try:
            # Try to find JSON in the response
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            
            if start_idx != -1 and end_idx > start_idx:
                json_str = response[start_idx:end_idx]
                result = json.loads(json_str)
                
                # Validate required fields
                if all(key in result for key in ["intent", "confidence", "reasoning"]):
                    # Ensure confidence is a float between 0 and 1
                    result["confidence"] = max(0.0, min(1.0, float(result["confidence"])))
                    return result
            
            raise ValueError("Invalid JSON format in response")
            
        except (json.JSONDecodeError, ValueError, KeyError) as e:
            # Fallback parsing for malformed responses
            return {
                "intent": IntentCategory.GENERAL.value,
                "confidence": 0.2,
                "reasoning": f"Failed to parse classification response: {str(e)}"
            }
    
    def get_agent_capabilities(self) -> Dict[AgentType, List[str]]:
        """Get a description of each agent's capabilities for routing decisions."""
        return {
            AgentType.RESEARCH: [
                "Web search and information retrieval",
                "Fact-checking and verification",
                "Literature and document analysis",
                "Knowledge base queries",
                "Market research and trends"
            ],
            AgentType.CODE: [
                "Programming in multiple languages",
                "Code debugging and optimization",
                "Architecture and design patterns",
                "Testing and quality assurance",
                "API development and integration"
            ],
            AgentType.WRITING: [
                "Content creation and editing",
                "Documentation and technical writing",
                "Creative writing and storytelling",
                "Communication and messaging",
                "Proofreading and style improvement"
            ],
            AgentType.DATA: [
                "Data analysis and statistics",
                "Data visualization and charts",
                "Database queries and manipulation",
                "Reporting and insights",
                "Machine learning and modeling"
            ],
            AgentType.SUPERVISOR: [
                "General conversation and coordination",
                "Task routing and orchestration",
                "Fallback for unclear requests",
                "Multi-agent workflow management"
            ]
        }
