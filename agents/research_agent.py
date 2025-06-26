"""
Research Agent for information gathering, web search, and knowledge retrieval tasks.
Specializes in finding, analyzing, and synthesizing information from various sources.
"""

from typing import List

from agents.base_agent import BaseAgent
from core.state import WorkflowState, AgentType
from utils.llm_client import LLMMessage


class ResearchAgent(BaseAgent):
    """Specialized agent for research and information gathering tasks."""
    
    def __init__(self):
        super().__init__(
            agent_type=AgentType.RESEARCH,
            name="Research Agent",
            description="Specializes in information gathering, fact-checking, and knowledge synthesis"
        )
    
    def get_system_prompt(self) -> str:
        """Get the system prompt for the research agent."""
        return """You are a Research Agent, an expert at information gathering and analysis. Your capabilities include:

CORE FUNCTIONS:
- Information research and fact-finding
- Web search strategy and source evaluation
- Literature review and academic research
- Market research and trend analysis
- Fact-checking and verification
- Knowledge synthesis and summarization

RESEARCH METHODOLOGY:
1. Break down complex questions into searchable components
2. Identify reliable and authoritative sources
3. Cross-reference information from multiple sources
4. Distinguish between facts, opinions, and speculation
5. Provide citations and source attribution when possible
6. Synthesize findings into coherent, actionable insights

SPECIALIZATIONS:
- Academic and scientific research
- Business and market intelligence
- Technical documentation and standards
- Historical and background information
- Current events and news analysis
- Comparative analysis and benchmarking

RESPONSE FORMAT:
- Start with a brief summary of key findings
- Provide detailed information organized logically
- Include source reliability assessment when relevant
- Suggest follow-up research if needed
- Clearly distinguish between verified facts and preliminary findings

LIMITATIONS:
- I cannot access real-time web search (note this in responses)
- I work with my training data and provided context
- I cannot verify very recent information (post-training cutoff)
- I recommend specific tools or databases for live research when appropriate

Always be thorough, accurate, and transparent about the limitations of available information."""
    
    def process_request(self, state: WorkflowState) -> WorkflowState:
        """
        Process research requests with specialized research methodology.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated workflow state
        """
        try:
            # Preprocess the research request
            state = self.preprocess_request(state)
            
            # Analyze the type of research needed
            research_type = self._analyze_research_type(state.current_user_input)
            
            # Build specialized research prompt
            messages = self._build_research_messages(state, research_type)
            
            # Generate research response
            response = self.generate_response(messages, temperature=0.3)  # Lower temp for accuracy
            
            # Postprocess with research formatting
            formatted_response = self.postprocess_response(state, response)
            
            # Update state with research results
            state.task_context['research_type'] = research_type
            state.task_context['sources_consulted'] = self._extract_sources(response)
            
            return self.update_state_with_response(state, formatted_response)
            
        except Exception as e:
            return self.handle_error(state, e)
    
    def _analyze_research_type(self, user_input: str) -> str:
        """
        Analyze what type of research is being requested.
        
        Args:
            user_input: User's research request
            
        Returns:
            Research type classification
        """
        input_lower = user_input.lower()
        
        if any(term in input_lower for term in ['fact check', 'verify', 'true', 'false', 'accurate']):
            return 'fact_checking'
        elif any(term in input_lower for term in ['market', 'industry', 'competition', 'trends']):
            return 'market_research'
        elif any(term in input_lower for term in ['academic', 'study', 'research paper', 'journal']):
            return 'academic_research'
        elif any(term in input_lower for term in ['how to', 'guide', 'tutorial', 'steps']):
            return 'instructional_research'
        elif any(term in input_lower for term in ['history', 'background', 'origin', 'development']):
            return 'historical_research'
        elif any(term in input_lower for term in ['compare', 'vs', 'versus', 'difference']):
            return 'comparative_research'
        else:
            return 'general_research'
    
    def _build_research_messages(self, state: WorkflowState, research_type: str) -> List[LLMMessage]:
        """
        Build specialized messages for research requests.
        
        Args:
            state: Current workflow state
            research_type: Type of research needed
            
        Returns:
            List of formatted messages
        """
        messages = [LLMMessage("system", self.get_system_prompt())]
        
        # Add research type specific guidance
        type_guidance = self._get_research_type_guidance(research_type)
        if type_guidance:
            messages.append(LLMMessage("system", f"SPECIFIC GUIDANCE FOR {research_type.upper()}:\n{type_guidance}"))
        
        # Add user request with context
        context = state.get_conversation_context()
        if context:
            user_message = f"Previous conversation:\n{context}\n\nResearch Request: {state.current_user_input}"
        else:
            user_message = f"Research Request: {state.current_user_input}"
        
        messages.append(LLMMessage("user", user_message))
        
        return messages
    
    def _get_research_type_guidance(self, research_type: str) -> str:
        """Get specific guidance for different research types."""
        guidance_map = {
            'fact_checking': """
- Focus on verifiable facts and authoritative sources
- Distinguish between confirmed facts and claims
- Note any conflicting information found
- Assess source credibility and potential bias
""",
            'market_research': """
- Look for market size, growth trends, and key players
- Include competitive landscape analysis
- Identify market opportunities and challenges
- Consider geographic and demographic factors
""",
            'academic_research': """
- Prioritize peer-reviewed and scholarly sources
- Include methodology and study limitations
- Present multiple perspectives when they exist
- Use proper academic citation style
""",
            'instructional_research': """
- Break down complex processes into clear steps
- Include prerequisites and required materials
- Highlight common mistakes or pitfalls
- Provide alternative approaches when available
""",
            'historical_research': """
- Present chronological development
- Include key events, dates, and figures
- Provide context for historical significance
- Note any historical debates or controversies
""",
            'comparative_research': """
- Create structured comparisons with clear criteria
- Highlight key similarities and differences
- Include pros and cons for each option
- Provide context for when each might be preferred
"""
        }
        return guidance_map.get(research_type, "")
    
    def _extract_sources(self, response: str) -> List[str]:
        """Extract mentioned sources from the research response."""
        sources = []
        # Simple extraction - look for common source indicators
        lines = response.split('\n')
        for line in lines:
            line_lower = line.lower()
            if any(indicator in line_lower for indicator in ['source:', 'reference:', 'study:', 'according to']):
                sources.append(line.strip())
        return sources
    
    def can_handle_request(self, user_input: str, intent: str) -> bool:
        """Check if this agent can handle the research request."""
        research_keywords = [
            'research', 'find', 'search', 'information', 'facts', 'data',
            'study', 'analysis', 'investigate', 'explore', 'discover',
            'verify', 'check', 'confirm', 'what is', 'how many', 'when did'
        ]
        
        input_lower = user_input.lower()
        return any(keyword in input_lower for keyword in research_keywords)
    
    def get_capabilities(self) -> List[str]:
        """Get research agent capabilities."""
        return [
            "Information research and fact-finding",
            "Academic and scientific literature review",
            "Market research and competitive analysis",
            "Fact-checking and verification",
            "Historical and background research",
            "Comparative analysis between options",
            "Knowledge synthesis and summarization",
            "Source evaluation and credibility assessment"
        ]
    
    def postprocess_response(self, state: WorkflowState, response: str) -> str:
        """Add research-specific formatting to the response."""
        # Add research disclaimer if not already present
        if "training data" not in response.lower() and "real-time" not in response.lower():
            disclaimer = "\n\n📝 **Research Note**: This analysis is based on my training data. For the most current information, I recommend consulting recent sources or specialized databases."
            response += disclaimer
        
        # Add research type context
        research_type = state.task_context.get('research_type', 'general_research')
        if research_type != 'general_research':
            type_note = f"\n\n🔍 **Research Type**: {research_type.replace('_', ' ').title()}"
            response += type_note
        
        return response
    
    def get_fallback_response(self, state: WorkflowState, error: Exception) -> str:
        """Generate fallback response for research errors."""
        return (
            "I apologize, but I encountered an issue while researching your request. "
            "This might be due to the complexity of the query or technical limitations. "
            "Could you try:\n"
            "1. Breaking your question into smaller, more specific parts\n"
            "2. Providing more context about what type of information you need\n"
            "3. Rephrasing your research question\n\n"
            "I'm here to help with your research needs once we resolve this issue."
        )
