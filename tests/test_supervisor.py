"""
Test suite for the supervisor agent functionality.
Tests routing logic, intent classification integration, and error handling.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import os

from agents.supervisor import SupervisorAgent
from agents.base_agent import BaseAgent
from core.state import WorkflowState, AgentType, MessageRole
from core.intent_classifier import IntentClassifier


class TestSupervisorAgent:
    """Test cases for the SupervisorAgent class."""
    
    @pytest.fixture
    def supervisor(self):
        """Create a supervisor agent instance for testing."""
        # Mock the LLM client to avoid API key requirements
        with patch('utils.llm_client.get_default_llm_client') as mock_llm:
            mock_llm.return_value = Mock()
            return SupervisorAgent()
    
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
        assert isinstance(supervisor.intent_classifier, IntentClassifier)
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
    
    @patch('agents.supervisor.IntentClassifier')
    def test_process_request_routing(self, mock_classifier_class, supervisor, mock_state, mock_agent):
        """Test request processing and routing logic."""
        # Setup mock classifier
        mock_classifier = Mock()
        mock_classifier.classify_intent.return_value = (
            "research", 0.8, "High confidence research request", AgentType.RESEARCH
        )
        mock_classifier_class.return_value = mock_classifier
        supervisor.intent_classifier = mock_classifier
        
        # Register mock agent
        supervisor.register_agent(mock_agent)
        
        # Process request
        result = supervisor.process_request(mock_state)
        
        # Verify classification was called
        mock_classifier.classify_intent.assert_called_once()
        
        # Verify state updates
        assert result.detected_intent == "research"
        assert result.intent_confidence == 0.8
        assert len(result.handoff_history) > 0
    
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
        with patch.object(supervisor, 'generate_response') as mock_generate:
            mock_generate.return_value = "Direct supervisor response"
            
            result = supervisor._handle_directly(mock_state)
            
            assert result.final_response == "Direct supervisor response"
            assert len(result.messages) > 0
            assert result.messages[-1].role == MessageRole.ASSISTANT
    
    def test_error_handling(self, supervisor, mock_state):
        """Test error handling in supervisor."""
        with patch.object(supervisor, 'generate_response') as mock_generate:
            mock_generate.side_effect = Exception("Test error")
            
            result = supervisor.process_request(mock_state)
            
            assert result.error_count > 0
            assert "error" in result.last_error.lower()
    
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
