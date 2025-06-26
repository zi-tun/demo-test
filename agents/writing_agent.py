"""
Writing Agent for content creation, editing, and communication tasks.
Specializes in various forms of written content from technical docs to creative writing.
"""

from typing import List

from agents.base_agent import BaseAgent
from core.state import WorkflowState, AgentType
from utils.llm_client import LLMMessage


class WritingAgent(BaseAgent):
    """Specialized agent for writing and content creation tasks."""
    
    def __init__(self):
        super().__init__(
            agent_type=AgentType.WRITING,
            name="Writing Agent",
            description="Specializes in content creation, editing, and written communication"
        )
    
    def get_system_prompt(self) -> str:
        """Get the system prompt for the writing agent."""
        return """You are a Writing Agent, an expert in content creation and written communication. Your capabilities include:

CORE WRITING FUNCTIONS:
- Content creation and copywriting
- Technical documentation and manuals
- Creative writing and storytelling
- Business communication and proposals
- Academic writing and research papers
- Editing and proofreading
- Style and tone adaptation

WRITING SPECIALIZATIONS:
- Blog posts and articles
- Marketing copy and advertisements
- Technical documentation
- User guides and tutorials
- Email templates and communication
- Social media content
- Press releases and announcements
- Creative fiction and poetry

WRITING BEST PRACTICES:
1. Adapt tone and style to target audience
2. Ensure clarity and conciseness
3. Maintain logical flow and structure
4. Use appropriate formatting and organization
5. Follow grammar and style conventions
6. Include engaging introductions and conclusions
7. Optimize for readability and accessibility

EDITING CRITERIA:
- Grammar and syntax correctness
- Clarity and coherence
- Tone and style consistency
- Logical flow and organization
- Factual accuracy and completeness
- Engagement and readability

RESPONSE APPROACH:
- Understand the purpose and audience
- Choose appropriate structure and format
- Use clear, engaging language
- Include relevant examples when helpful
- Suggest improvements and alternatives
- Maintain professional quality standards

Always prioritize clear communication, audience engagement, and professional quality in all written content."""
    
    def process_request(self, state: WorkflowState) -> WorkflowState:
        """Process writing requests with specialized content creation methodology."""
        try:
            # Analyze the writing task
            writing_type = self._analyze_writing_task(state.current_user_input)
            target_audience = self._identify_target_audience(state.current_user_input)
            
            # Build specialized writing prompt
            messages = self._build_writing_messages(state, writing_type, target_audience)
            
            # Generate content with appropriate creativity
            temperature = 0.8 if writing_type in ['creative', 'marketing'] else 0.6
            response = self.generate_response(messages, temperature=temperature)
            
            # Postprocess with writing-specific formatting
            formatted_response = self.postprocess_response(state, response)
            
            # Update state with writing context
            state.task_context['writing_type'] = writing_type
            state.task_context['target_audience'] = target_audience
            
            return self.update_state_with_response(state, formatted_response)
            
        except Exception as e:
            return self.handle_error(state, e)
    
    def _analyze_writing_task(self, user_input: str) -> str:
        """Analyze what type of writing task is being requested."""
        input_lower = user_input.lower()
        
        if any(term in input_lower for term in ['blog', 'article', 'post']):
            return 'blog_article'
        elif any(term in input_lower for term in ['email', 'message', 'letter']):
            return 'email_communication'
        elif any(term in input_lower for term in ['documentation', 'manual', 'guide', 'tutorial']):
            return 'technical_documentation'
        elif any(term in input_lower for term in ['marketing', 'advertisement', 'copy', 'promotional']):
            return 'marketing_copy'
        elif any(term in input_lower for term in ['story', 'creative', 'fiction', 'narrative']):
            return 'creative'
        elif any(term in input_lower for term in ['business', 'proposal', 'report', 'formal']):
            return 'business_writing'
        elif any(term in input_lower for term in ['edit', 'proofread', 'improve', 'revise']):
            return 'editing'
        elif any(term in input_lower for term in ['social media', 'tweet', 'post', 'caption']):
            return 'social_media'
        else:
            return 'general_writing'
    
    def _identify_target_audience(self, user_input: str) -> str:
        """Identify the target audience for the writing."""
        input_lower = user_input.lower()
        
        if any(term in input_lower for term in ['technical', 'developer', 'engineer']):
            return 'technical_professional'
        elif any(term in input_lower for term in ['business', 'executive', 'corporate']):
            return 'business_professional'
        elif any(term in input_lower for term in ['academic', 'research', 'scholarly']):
            return 'academic'
        elif any(term in input_lower for term in ['customer', 'client', 'user']):
            return 'end_user'
        elif any(term in input_lower for term in ['general', 'public', 'everyone']):
            return 'general_public'
        else:
            return 'general'
    
    def _build_writing_messages(self, state: WorkflowState, writing_type: str, target_audience: str) -> List[LLMMessage]:
        """Build specialized messages for writing requests."""
        messages = [LLMMessage("system", self.get_system_prompt())]
        
        # Add writing-specific guidance
        type_guidance = self._get_writing_type_guidance(writing_type, target_audience)
        if type_guidance:
            messages.append(LLMMessage("system", f"SPECIFIC GUIDANCE FOR {writing_type.upper()}:\n{type_guidance}"))
        
        # Add user request with context
        context = state.get_conversation_context()
        if context:
            user_message = f"Previous conversation:\n{context}\n\nWriting Request: {state.current_user_input}"
        else:
            user_message = f"Writing Request: {state.current_user_input}"
        
        messages.append(LLMMessage("user", user_message))
        
        return messages
    
    def _get_writing_type_guidance(self, writing_type: str, target_audience: str) -> str:
        """Get specific guidance for different writing types."""
        guidance_map = {
            'blog_article': """
- Start with an engaging hook to capture attention
- Use clear headings and subheadings for structure
- Include relevant examples and actionable insights
- Optimize for readability with short paragraphs
- End with a compelling conclusion or call-to-action
""",
            'technical_documentation': """
- Use clear, precise language without jargon
- Include step-by-step instructions where applicable
- Add code examples or screenshots when relevant
- Structure with logical hierarchy and navigation
- Include troubleshooting and FAQ sections
""",
            'marketing_copy': """
- Focus on benefits rather than features
- Use persuasive language and emotional triggers
- Include clear value propositions
- Add compelling calls-to-action
- Maintain brand voice and messaging consistency
""",
            'creative': """
- Develop engaging characters and settings
- Use vivid imagery and descriptive language
- Build narrative tension and pacing
- Show rather than tell when possible
- Create emotional connection with readers
""",
            'business_writing': """
- Use professional tone and formal structure
- Be concise and results-oriented
- Include executive summary for longer pieces
- Support arguments with data and evidence
- Follow standard business communication formats
""",
            'editing': """
- Check for grammar, spelling, and punctuation
- Improve clarity and conciseness
- Ensure consistent tone and style
- Verify factual accuracy and completeness
- Enhance flow and readability
"""
        }
        
        guidance = guidance_map.get(writing_type, "")
        
        # Add audience-specific guidance
        if target_audience != 'general':
            guidance += f"\n- Tailor language and complexity for {target_audience.replace('_', ' ')}"
            guidance += f"\n- Consider the specific needs and expectations of {target_audience.replace('_', ' ')}"
        
        return guidance
    
    def can_handle_request(self, user_input: str, intent: str) -> bool:
        """Check if this agent can handle the writing request."""
        writing_keywords = [
            'write', 'create', 'draft', 'compose', 'edit', 'proofread',
            'blog', 'article', 'email', 'letter', 'documentation', 'guide',
            'story', 'content', 'copy', 'marketing', 'social media'
        ]
        
        input_lower = user_input.lower()
        return any(keyword in input_lower for keyword in writing_keywords)
    
    def get_capabilities(self) -> List[str]:
        """Get writing agent capabilities."""
        return [
            "Blog posts and articles",
            "Technical documentation and guides",
            "Business communication and proposals",
            "Marketing copy and advertisements",
            "Email templates and messages",
            "Creative writing and storytelling",
            "Content editing and proofreading",
            "Social media content",
            "Academic writing assistance",
            "Style and tone adaptation"
        ]
    
    def postprocess_response(self, state: WorkflowState, response: str) -> str:
        """Add writing-specific formatting to the response."""
        writing_type = state.task_context.get('writing_type', 'general_writing')
        target_audience = state.task_context.get('target_audience', 'general')
        
        # Add writing context note
        if writing_type != 'general_writing' or target_audience != 'general':
            context_note = f"\n\n✍️ **Writing Context**: {writing_type.replace('_', ' ').title()}"
            if target_audience != 'general':
                context_note += f" for {target_audience.replace('_', ' ').title()}"
            response += context_note
        
        # Add editing reminder for content creation
        if writing_type in ['blog_article', 'marketing_copy', 'business_writing']:
            editing_note = "\n\n📝 **Note**: Please review and customize this content for your specific needs, brand voice, and requirements."
            response += editing_note
        
        return response
    
    def get_fallback_response(self, state: WorkflowState, error: Exception) -> str:
        """Generate fallback response for writing errors."""
        return (
            "I apologize, but I encountered an issue while working on your writing request. "
            "This might be due to the complexity of the task or technical limitations. "
            "Could you try:\n"
            "1. Providing more specific details about the content you need\n"
            "2. Clarifying the target audience and purpose\n"
            "3. Breaking down complex requests into smaller tasks\n"
            "4. Specifying the desired tone, style, or format\n\n"
            "I'm here to help with your writing needs once we resolve this issue."
        )
