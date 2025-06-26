"""
Main entry point for the LangGraph multi-agent orchestration system.
Provides CLI interface and demonstrates the multi-agent workflow.
"""

import os
import sys
from typing import Optional
import argparse
from dotenv import load_dotenv

from core.graph_builder import MultiAgentGraphBuilder
from core.state import WorkflowState
from utils.error_handler import ErrorHandler, GracefulDegradation
from config.settings import Settings
import tools  # This will auto-register tools


def setup_environment():
    """Load environment variables and validate configuration."""
    # Load environment variables
    load_dotenv()
    
    # Check for demo mode
    if os.getenv("DEMO_MODE", "").lower() in ["true", "1", "yes"]:
        print("🎭 Demo Mode: Running with mock responses (no real API calls)")
        return True
    
    # Check for required API keys
    has_openai = bool(os.getenv("OPENAI_API_KEY"))
    has_anthropic = bool(os.getenv("ANTHROPIC_API_KEY"))
    
    # Check for Cisco OpenAI configuration
    has_cisco_openai = False
    try:
        from utils.llm_client import CiscoOpenAIClient
        cisco_client = CiscoOpenAIClient()
        has_cisco_openai = cisco_client.is_available()
    except:
        has_cisco_openai = False
    
    if not has_openai and not has_anthropic and not has_cisco_openai:
        print("⚠️  Warning: No LLM API keys found!")
        print("Please set either OPENAI_API_KEY or ANTHROPIC_API_KEY in your .env file")
        print("Or configure Cisco OpenAI in config/openai.properties")
        print("Copy .env.example to .env and add your API keys")
        print("Or set DEMO_MODE=true in .env to run with mock responses")
        return False
    
    if has_openai:
        print("✅ OpenAI API key found")
    if has_anthropic:
        print("✅ Anthropic API key found")
    if has_cisco_openai:
        print("✅ Cisco Enterprise OpenAI configured")
    
    return True


class MultiAgentCLI:
    """Command-line interface for the multi-agent system."""
    
    def __init__(self):
        """Initialize the CLI with graph builder and error handling."""
        self.settings = Settings()
        self.graph_builder = MultiAgentGraphBuilder()
        self.error_handler = ErrorHandler(
            max_retries=self.settings.max_retries,
            enable_fallback=True
        )
        self.degradation = GracefulDegradation(self.error_handler)
        self.session_history = []
    
    def run_interactive(self):
        """Run interactive CLI session."""
        print("🤖 LangGraph Multi-Agent Orchestration System")
        print("=" * 50)
        print("Available agents: Research, Code, Writing, Data, Supervisor")
        print("Type 'help' for commands, 'quit' to exit")
        print()
        
        # Build the workflow graph
        try:
            self.graph_builder.build_graph()
            print("✅ Multi-agent workflow initialized successfully")
        except Exception as e:
            print(f"❌ Failed to initialize workflow: {str(e)}")
            print("Please check your dependencies and configuration")
            return
        
        print()
        
        while True:
            try:
                # Get user input
                user_input = input("👤 You: ").strip()
                
                if not user_input:
                    continue
                
                # Handle special commands
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye!")
                    break
                elif user_input.lower() == 'help':
                    self._show_help()
                    continue
                elif user_input.lower() == 'status':
                    self._show_status()
                    continue
                elif user_input.lower() == 'clear':
                    self._clear_session()
                    continue
                elif user_input.lower() == 'agents':
                    self._show_agents()
                    continue
                elif user_input.lower() == 'tools':
                    self._show_tools()
                    continue
                
                # Process user input through the workflow
                print("🔄 Processing...")
                response = self._process_input(user_input)
                
                # Display response
                print(f"🤖 Assistant: {response}")
                print()
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Unexpected error: {str(e)}")
                print("Please try again or type 'quit' to exit")
    
    def run_single_query(self, query: str) -> str:
        """
        Process a single query and return the response.
        
        Args:
            query: User query to process
            
        Returns:
            Agent response
        """
        try:
            self.graph_builder.build_graph()
            return self._process_input(query)
        except Exception as e:
            return f"Error processing query: {str(e)}"
    
    def _process_input(self, user_input: str) -> str:
        """
        Process user input through the multi-agent workflow.
        
        Args:
            user_input: User's input message
            
        Returns:
            Final response from the system
        """
        try:
            # Process through the workflow
            final_state = self.graph_builder.process_user_input(user_input)
            
            # Apply graceful degradation if needed
            if final_state.error_count > 0:
                final_state = self.degradation.apply_degradation(final_state)
            
            # Add to session history
            self.session_history.append({
                'input': user_input,
                'response': final_state.final_response,
                'agent_used': final_state.current_agent.value,
                'intent': final_state.detected_intent,
                'confidence': final_state.intent_confidence,
                'errors': final_state.error_count
            })
            
            return final_state.final_response
            
        except Exception as e:
            error_msg = f"I apologize, but I encountered an error: {str(e)}"
            self.session_history.append({
                'input': user_input,
                'response': error_msg,
                'agent_used': 'error',
                'intent': None,
                'confidence': 0.0,
                'errors': 1
            })
            return error_msg
    
    def _show_help(self):
        """Display help information."""
        print("\n📖 Available Commands:")
        print("  help     - Show this help message")
        print("  status   - Show system status and degradation level")
        print("  agents   - Show available agents and their capabilities")
        print("  tools    - Show available tools and their descriptions")
        print("  clear    - Clear session history")
        print("  quit     - Exit the application")
        print("\n💡 Tips:")
        print("  - Ask questions naturally - the system will route to the best agent")
        print("  - For coding help, mention the programming language")
        print("  - For research, be specific about what information you need")
        print("  - For writing, specify the type of content and audience")
        print("  - Each agent has access to specialized tools for their domain")
        print()
    
    def _show_status(self):
        """Display system status."""
        degradation_status = self.degradation.get_degradation_status()
        
        print(f"\n📊 System Status:")
        print(f"  Degradation Level: {degradation_status['current_level']}")
        print(f"  Description: {degradation_status['description']}")
        print(f"  Session Queries: {len(self.session_history)}")
        
        if self.session_history:
            recent = self.session_history[-1]
            print(f"  Last Agent Used: {recent['agent_used']}")
            if recent['intent']:
                print(f"  Last Intent: {recent['intent']} (confidence: {recent['confidence']:.2f})")
        
        print()
    
    def _show_agents(self):
        """Display agent information."""
        workflow_summary = self.graph_builder.get_workflow_summary()
        
        print("\n🤖 Available Agents:")
        for agent_name, info in workflow_summary['agents'].items():
            print(f"\n  {info['name']}:")
            print(f"    Description: {info['description']}")
            print("    Capabilities:")
            for capability in info['capabilities'][:3]:  # Show top 3 capabilities
                print(f"      • {capability}")
            if len(info['capabilities']) > 3:
                print(f"      ... and {len(info['capabilities']) - 3} more")
        print()
    
    def _show_tools(self):
        """Display available tools information."""
        from core.tool_discovery import get_tool_registry
        
        registry = get_tool_registry()
        tools = registry.list_all_tools()
        
        print(f"\n🔧 Available Tools ({len(tools)} total):")
        
        # Group tools by category
        from collections import defaultdict
        tools_by_category = defaultdict(list)
        for tool in tools:
            tools_by_category[tool.metadata.category.value].append(tool)
        
        for category, category_tools in tools_by_category.items():
            if category_tools:
                print(f"\n  📂 {category.title()} Tools:")
                for tool in category_tools:
                    agents = ", ".join(tool.metadata.agent_types)
                    print(f"    • {tool.metadata.name}: {tool.metadata.description}")
                    print(f"      Compatible with: {agents}")
        
        print("\n💡 Use 'python tool_discovery_cli.py show <tool_name>' for detailed tool information")
        print()
    
    def _clear_session(self):
        """Clear session history."""
        self.session_history.clear()
        self.graph_builder.reset_memory()
        print("🧹 Session history cleared")


def main():
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(description="LangGraph Multi-Agent Orchestration System")
    parser.add_argument("--query", "-q", type=str, help="Process a single query and exit")
    parser.add_argument("--interactive", "-i", action="store_true", default=True,
                       help="Run in interactive mode (default)")
    parser.add_argument("--version", "-v", action="version", version="1.0.0")
    
    args = parser.parse_args()
    
    # Setup environment
    if not setup_environment():
        sys.exit(1)
    
    # Initialize CLI
    try:
        cli = MultiAgentCLI()
    except Exception as e:
        print(f"❌ Failed to initialize application: {str(e)}")
        sys.exit(1)
    
    # Run based on arguments
    if args.query:
        # Single query mode
        print("🤖 LangGraph Multi-Agent System - Single Query Mode")
        print("=" * 50)
        response = cli.run_single_query(args.query)
        print(f"Query: {args.query}")
        print(f"Response: {response}")
    else:
        # Interactive mode
        cli.run_interactive()


if __name__ == "__main__":
    main()
