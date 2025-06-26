"""
Code Agent for programming tasks, debugging, and software development assistance.
Specializes in code generation, review, debugging, and technical implementation.
"""

from typing import List

from agents.base_agent import BaseAgent
from core.state import WorkflowState, AgentType
from utils.llm_client import LLMMessage


class CodeAgent(BaseAgent):
    """Specialized agent for programming and software development tasks."""
    
    def __init__(self):
        super().__init__(
            agent_type=AgentType.CODE,
            name="Code Agent",
            description="Specializes in programming, debugging, and software development"
        )
    
    def get_system_prompt(self) -> str:
        """Get the system prompt for the code agent."""
        return """You are a Code Agent, an expert software engineer and programming assistant. Your capabilities include:

CORE PROGRAMMING FUNCTIONS:
- Code generation in multiple programming languages
- Debugging and error resolution
- Code review and optimization
- Architecture and design pattern guidance
- Testing and quality assurance
- API development and integration

SUPPORTED LANGUAGES & TECHNOLOGIES:
- Python, JavaScript/TypeScript, Java, C++, C#, Go, Rust
- Web frameworks: React, Vue, Angular, Node.js, Django, Flask
- Mobile: React Native, Flutter, Swift, Kotlin
- Databases: SQL, NoSQL, PostgreSQL, MongoDB
- Cloud platforms: AWS, Azure, GCP
- DevOps: Docker, Kubernetes, CI/CD

PROGRAMMING BEST PRACTICES:
1. Write clean, readable, and maintainable code
2. Follow language-specific conventions and style guides
3. Include proper error handling and edge cases
4. Add meaningful comments and documentation
5. Consider security implications and best practices
6. Optimize for performance when appropriate
7. Write testable code with clear separation of concerns

CODE REVIEW CRITERIA:
- Functionality and correctness
- Code structure and organization
- Performance and efficiency
- Security vulnerabilities
- Maintainability and readability
- Testing coverage and quality

RESPONSE FORMAT:
- Provide working, tested code examples
- Include clear explanations of implementation choices
- Add comments for complex logic
- Suggest improvements and alternatives
- Include usage examples when relevant
- Highlight potential issues or limitations

DEBUGGING APPROACH:
1. Analyze error messages and stack traces
2. Identify root causes vs. symptoms
3. Provide step-by-step debugging strategies
4. Suggest preventive measures
5. Recommend debugging tools and techniques

Always prioritize code quality, security, and maintainability while providing practical, working solutions."""
    
    def process_request(self, state: WorkflowState) -> WorkflowState:
        """
        Process coding requests with specialized development methodology.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated workflow state
        """
        try:
            # Preprocess the coding request
            state = self.preprocess_request(state)
            
            # Analyze the type of coding task
            task_type = self._analyze_coding_task(state.current_user_input)
            
            # Extract programming language if specified
            language = self._extract_programming_language(state.current_user_input)
            
            # Build specialized coding prompt
            messages = self._build_coding_messages(state, task_type, language)
            
            # Generate code response with appropriate temperature
            temperature = 0.2 if task_type in ['debugging', 'code_review'] else 0.3
            response = self.generate_response(messages, temperature=temperature)
            
            # Postprocess with code formatting
            formatted_response = self.postprocess_response(state, response)
            
            # Update state with coding context
            state.task_context['coding_task_type'] = task_type
            state.task_context['programming_language'] = language
            state.task_context['code_blocks'] = self._extract_code_blocks(response)
            
            return self.update_state_with_response(state, formatted_response)
            
        except Exception as e:
            return self.handle_error(state, e)
    
    def _analyze_coding_task(self, user_input: str) -> str:
        """
        Analyze what type of coding task is being requested.
        
        Args:
            user_input: User's coding request
            
        Returns:
            Coding task type classification
        """
        input_lower = user_input.lower()
        
        if any(term in input_lower for term in ['debug', 'error', 'fix', 'bug', 'issue', 'problem']):
            return 'debugging'
        elif any(term in input_lower for term in ['review', 'improve', 'optimize', 'refactor']):
            return 'code_review'
        elif any(term in input_lower for term in ['test', 'unit test', 'testing', 'pytest', 'jest']):
            return 'testing'
        elif any(term in input_lower for term in ['api', 'endpoint', 'rest', 'graphql', 'service']):
            return 'api_development'
        elif any(term in input_lower for term in ['database', 'sql', 'query', 'schema']):
            return 'database'
        elif any(term in input_lower for term in ['algorithm', 'data structure', 'complexity']):
            return 'algorithms'
        elif any(term in input_lower for term in ['web', 'frontend', 'ui', 'html', 'css']):
            return 'web_development'
        elif any(term in input_lower for term in ['deploy', 'docker', 'kubernetes', 'ci/cd']):
            return 'devops'
        else:
            return 'general_coding'
    
    def _extract_programming_language(self, user_input: str) -> str:
        """Extract programming language from user input."""
        input_lower = user_input.lower()
        
        language_patterns = {
            'python': ['python', 'py', 'django', 'flask', 'pandas', 'numpy'],
            'javascript': ['javascript', 'js', 'node', 'react', 'vue', 'angular'],
            'typescript': ['typescript', 'ts'],
            'java': ['java', 'spring', 'maven', 'gradle'],
            'cpp': ['c++', 'cpp', 'cxx'],
            'csharp': ['c#', 'csharp', '.net', 'dotnet'],
            'go': ['go', 'golang'],
            'rust': ['rust', 'cargo'],
            'sql': ['sql', 'postgresql', 'mysql', 'sqlite'],
            'html': ['html', 'markup'],
            'css': ['css', 'scss', 'sass'],
        }
        
        for language, patterns in language_patterns.items():
            if any(pattern in input_lower for pattern in patterns):
                return language
        
        return 'general'
    
    def _build_coding_messages(self, state: WorkflowState, task_type: str, language: str) -> List[LLMMessage]:
        """
        Build specialized messages for coding requests.
        
        Args:
            state: Current workflow state
            task_type: Type of coding task
            language: Programming language
            
        Returns:
            List of formatted messages
        """
        messages = [LLMMessage("system", self.get_system_prompt())]
        
        # Add task-specific guidance
        task_guidance = self._get_task_type_guidance(task_type, language)
        if task_guidance:
            messages.append(LLMMessage("system", f"SPECIFIC GUIDANCE FOR {task_type.upper()}:\n{task_guidance}"))
        
        # Add user request with context
        context = state.get_conversation_context()
        if context:
            user_message = f"Previous conversation:\n{context}\n\nCoding Request: {state.current_user_input}"
        else:
            user_message = f"Coding Request: {state.current_user_input}"
        
        messages.append(LLMMessage("user", user_message))
        
        return messages
    
    def _get_task_type_guidance(self, task_type: str, language: str) -> str:
        """Get specific guidance for different coding task types."""
        base_guidance = {
            'debugging': """
- Carefully analyze error messages and stack traces
- Identify the root cause, not just symptoms
- Provide step-by-step debugging approach
- Include print statements or logging for diagnosis
- Suggest preventive measures for the future
""",
            'code_review': """
- Focus on code quality, readability, and maintainability
- Check for security vulnerabilities and edge cases
- Suggest performance optimizations where applicable
- Ensure proper error handling and documentation
- Recommend best practices and design patterns
""",
            'testing': """
- Write comprehensive test cases covering edge cases
- Include unit tests, integration tests as appropriate
- Use proper testing frameworks and assertions
- Focus on test coverage and maintainability
- Include setup and teardown procedures
""",
            'api_development': """
- Design RESTful or GraphQL APIs following conventions
- Include proper error handling and status codes
- Add input validation and sanitization
- Consider authentication and authorization
- Document API endpoints and parameters
""",
            'algorithms': """
- Analyze time and space complexity
- Provide multiple solution approaches when possible
- Include explanation of algorithm logic
- Add test cases with expected outputs
- Consider edge cases and performance
"""
        }
        
        guidance = base_guidance.get(task_type, "")
        
        # Add language-specific guidance
        if language != 'general':
            guidance += f"\n- Follow {language} best practices and conventions"
            guidance += f"\n- Use appropriate {language} libraries and frameworks"
        
        return guidance
    
    def _extract_code_blocks(self, response: str) -> List[str]:
        """Extract code blocks from the response for analysis."""
        code_blocks = []
        lines = response.split('\n')
        in_code_block = False
        current_block = []
        
        for line in lines:
            if line.strip().startswith('```'):
                if in_code_block:
                    code_blocks.append('\n'.join(current_block))
                    current_block = []
                    in_code_block = False
                else:
                    in_code_block = True
            elif in_code_block:
                current_block.append(line)
        
        return code_blocks
    
    def can_handle_request(self, user_input: str, intent: str) -> bool:
        """Check if this agent can handle the coding request."""
        coding_keywords = [
            'code', 'program', 'function', 'class', 'method', 'variable',
            'algorithm', 'debug', 'error', 'bug', 'test', 'api', 'database',
            'javascript', 'python', 'java', 'c++', 'sql', 'html', 'css'
        ]
        
        input_lower = user_input.lower()
        return any(keyword in input_lower for keyword in coding_keywords)
    
    def get_capabilities(self) -> List[str]:
        """Get code agent capabilities."""
        return [
            "Code generation in multiple programming languages",
            "Debugging and error resolution",
            "Code review and optimization",
            "Algorithm design and implementation",
            "API development and integration",
            "Database design and queries",
            "Testing and quality assurance",
            "Web development (frontend and backend)",
            "DevOps and deployment assistance",
            "Architecture and design pattern guidance"
        ]
    
    def postprocess_response(self, state: WorkflowState, response: str) -> str:
        """Add code-specific formatting to the response."""
        # Add execution note for code examples
        if '```' in response:
            execution_note = "\n\n💻 **Execution Note**: Please test the code in your development environment and adjust as needed for your specific use case."
            response += execution_note
        
        # Add task type context
        task_type = state.task_context.get('coding_task_type', 'general_coding')
        language = state.task_context.get('programming_language', 'general')
        
        if task_type != 'general_coding' or language != 'general':
            context_note = f"\n\n🔧 **Task Context**: {task_type.replace('_', ' ').title()}"
            if language != 'general':
                context_note += f" in {language.title()}"
            response += context_note
        
        return response
    
    def get_fallback_response(self, state: WorkflowState, error: Exception) -> str:
        """Generate fallback response for coding errors."""
        return (
            "I apologize, but I encountered an issue while processing your coding request. "
            "This might be due to the complexity of the problem or technical limitations. "
            "Could you try:\n"
            "1. Breaking down your request into smaller, specific tasks\n"
            "2. Providing more context about your programming environment\n"
            "3. Including relevant code snippets or error messages\n"
            "4. Specifying the programming language and framework\n\n"
            "I'm here to help with your development needs once we resolve this issue."
        )
