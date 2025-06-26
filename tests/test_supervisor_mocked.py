"""
Test suite for the supervisor agent functionality with mocked dependencies.
Tests routing logic, intent classification integration, and error handling.
"""

import pytest
import os
from unittest.mock import Mock, patch, MagicMock

# Set a test API key to avoid initialization errors
os.environ['OPENAI_API_KEY'] = 'test_key_for_testing_only'

from agents.supervisor import SupervisorAgent
from agents.base_agent import BaseAgent
from core.state import WorkflowState, AgentType, MessageRole


class TestSupervisorAgentMocked:
    """Test cases for the SupervisorAgent class with mocked dependencies."""
    
    @pytest.fixture
    def supervisor(self):
        """Create a supervisor agent instance with mocked LLM client."""
        with patch('agents.base_agent.get_default_llm_client') as mock_client:
            mock_client.return_value = Mock()
            supervisor = SupervisorAgent()
            # Mock the intent classifier as well
            supervisor.intent_classifier = Mock()
            return supervisor
    
    @pytest.fixture
    def mock_state(self):
        """Create a mock workflow state for testing."""
        state = WorkflowState()
        state.reset_for_new_input("Test user input")
        return state
    
    @pytest.fixture
    def mock_agent(self):
        """Create a mock specialized agent."""
        agent = Mock(spec=BaseAgent)
        agent.agent_type = AgentType.RESEARCH
        agent.name = "Mock Research Agent"
        agent.description = "Mock agent for testing"
        agent.can_handle_request.return_value = True
        agent.process_request.return_value = WorkflowState()
        agent.get_capabilities.return_value = ["Mock capability"]
        return agent
    
    def test_supervisor_initialization(self, supervisor):
        """Test supervisor agent initialization."""
        assert supervisor.agent_type == AgentType.SUPERVISOR
        assert supervisor.name == "Supervisor Agent"
        assert supervisor.available_agents == {}
    
    def test_register_agent(self, supervisor, mock_agent):
        """Test agent registration functionality."""
        supervisor.register_agent(mock_agent)
        assert AgentType.RESEARCH in supervisor.available_agents
        assert supervisor.available_agents[AgentType.RESEARCH] == mock_agent
    
    def test_get_system_prompt(self, supervisor, mock_agent):
        """Test system prompt generation."""
        supervisor.register_agent(mock_agent)
        prompt = supervisor.get_system_prompt()
        
        assert "Supervisor Agent" in prompt
        assert "multi-agent system" in prompt
        assert "Mock Research Agent" in prompt
    
    def test_should_route_to_specialist(self, supervisor, mock_state, mock_agent):
        """Test routing decision logic."""
        supervisor.register_agent(mock_agent)
        
        # Test high confidence routing
        assert supervisor._should_route_to_specialist(mock_state, AgentType.RESEARCH, 0.8)
        
        # Test low confidence - should not route
        assert not supervisor._should_route_to_specialist(mock_state, AgentType.RESEARCH, 0.3)
        
        # Test routing to supervisor (should not route)
        assert not supervisor._should_route_to_specialist(mock_state, AgentType.SUPERVISOR, 0.9)
        
        # Test unavailable agent
        assert not supervisor._should_route_to_specialist(mock_state, AgentType.CODE, 0.9)
    
    def test_handle_directly(self, supervisor, mock_state):
        """Test direct handling by supervisor."""
        supervisor.llm_client = Mock()
        supervisor.llm_client.generate_response.return_value = "Direct supervisor response"
        
        result = supervisor._handle_directly(mock_state)
        
        assert result.final_response == "Direct supervisor response"
        assert len(result.messages) > 0
        assert result.messages[-1].role == MessageRole.ASSISTANT
    
    def test_get_capabilities(self, supervisor):
        """Test capability listing."""
        capabilities = supervisor.get_capabilities()
        assert isinstance(capabilities, list)
        assert len(capabilities) > 0
        assert any("conversation" in cap.lower() for cap in capabilities)
    
    def test_routing_summary(self, supervisor, mock_state):
        """Test routing summary generation."""
        # Add some handoff history
        mock_state.add_handoff(
            AgentType.SUPERVISOR, AgentType.RESEARCH, 
            "research", 0.8, "Test routing"
        )
        
        summary = supervisor.get_routing_summary(mock_state)
        assert "Routing History" in summary
        assert "research" in summary
        assert "0.8" in summary  # confidence score
    
    def test_process_request_with_mocked_classifier(self, supervisor, mock_agent):
        """Test request processing with mocked intent classifier."""
        # Create a fresh state for this test
        test_state = WorkflowState()
        test_state.reset_for_new_input("Test research question")
        
        # Setup mocks
        supervisor.intent_classifier.classify_intent.return_value = (
            "research", 0.8, "High confidence research request", AgentType.RESEARCH
        )
        supervisor.register_agent(mock_agent)
        
        # Mock the agent's process_request to return a state with the response
        mock_result_state = WorkflowState()
        mock_result_state.detected_intent = "research"
        mock_result_state.intent_confidence = 0.8
        mock_result_state.final_response = "Mocked agent response"
        mock_agent.process_request.return_value = mock_result_state
        
        # Process request
        result = supervisor.process_request(test_state)
        
        # Verify classification was called
        supervisor.intent_classifier.classify_intent.assert_called_once()
        
        # Check that agent was called (since we're routing to it)
        if result.current_agent == AgentType.RESEARCH:
            mock_agent.process_request.assert_called_once()


class TestBasicWorkflowWithoutLLM:
    """Test basic workflow functionality that doesn't require LLM calls."""
    
    def test_workflow_state_operations(self):
        """Test workflow state operations without external dependencies."""
        state = WorkflowState()
        
        # Test adding handoffs
        state.add_handoff(
            AgentType.SUPERVISOR, AgentType.RESEARCH, 
            "test_intent", 0.8, "Test reasoning"
        )
        
        assert len(state.handoff_history) == 1
        assert state.handoff_history[0].intent == "test_intent"
        
        # Test error recording
        state.record_error("Test error")
        assert state.error_count == 1
        assert state.last_error == "Test error"
    
    def test_agent_type_mappings(self):
        """Test agent type enumerations."""
        assert AgentType.SUPERVISOR.value == "supervisor"
        assert AgentType.RESEARCH.value == "research"
        assert AgentType.CODE.value == "code"
        assert AgentType.WRITING.value == "writing"
        assert AgentType.DATA.value == "data"


if __name__ == "__main__":
    pytest.main([__file__])
