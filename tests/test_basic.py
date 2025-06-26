"""
Basic tests for configuration and system setup.
Tests that don't require API keys or external services.
"""

import pytest
import os
from unittest.mock import Mock, patch

from core.state import WorkflowState, AgentType, MessageRole
from config.config_reader import ConfigReader, OAuthCredentials


class TestBasicFunctionality:
    """Test basic system functionality without external dependencies."""
    
    def test_workflow_state_initialization(self):
        """Test WorkflowState initialization and basic operations."""
        state = WorkflowState()
        
        # Test initial state
        assert state.messages == []
        assert state.current_agent == AgentType.SUPERVISOR
        assert state.error_count == 0
        assert state.should_continue == True
        
        # Test adding messages
        state.add_message(MessageRole.USER, "Test message")
        assert len(state.messages) == 1
        assert state.messages[0].content == "Test message"
        assert state.messages[0].role == MessageRole.USER
    
    def test_workflow_state_reset(self):
        """Test workflow state reset functionality."""
        state = WorkflowState()
        state.add_message(MessageRole.USER, "Test")
        state.error_count = 5
        
        # Reset for new input
        state.reset_for_new_input("New input")
        
        assert state.current_user_input == "New input"
        assert state.current_agent == AgentType.SUPERVISOR
        assert state.should_continue == True
        assert state.final_response is None
    
    def test_agent_handoff_tracking(self):
        """Test agent handoff tracking."""
        state = WorkflowState()
        
        state.add_handoff(
            AgentType.SUPERVISOR, 
            AgentType.RESEARCH, 
            "research_intent", 
            0.8, 
            "High confidence research request"
        )
        
        assert len(state.handoff_history) == 1
        handoff = state.handoff_history[0]
        assert handoff.from_agent == AgentType.SUPERVISOR
        assert handoff.to_agent == AgentType.RESEARCH
        assert handoff.confidence == 0.8
    
    def test_error_recording(self):
        """Test error recording and fallback mode."""
        state = WorkflowState()
        
        # Record some errors
        state.record_error("Error 1")
        state.record_error("Error 2")
        state.record_error("Error 3")
        
        assert state.error_count == 3
        assert state.last_error == "Error 3"
        assert state.fallback_mode == True  # Should enable after 3 errors
    
    def test_conversation_context(self):
        """Test conversation context generation."""
        state = WorkflowState()
        
        state.add_message(MessageRole.USER, "Hello")
        state.add_message(MessageRole.ASSISTANT, "Hi there", AgentType.SUPERVISOR)
        state.add_message(MessageRole.USER, "How are you?")
        
        context = state.get_conversation_context(max_messages=2)
        
        assert "Hi there" in context
        assert "How are you?" in context
        assert "[supervisor]" in context.lower()


class TestConfigReader:
    """Test configuration reading functionality."""
    
    def test_oauth_credentials_creation(self):
        """Test OAuth credentials dataclass."""
        creds = OAuthCredentials(
            client_id="test_id",
            client_secret="test_secret", 
            app_key="test_key",
            grant_type="client_credentials",
            token_url="https://example.com/token"
        )
        
        assert creds.client_id == "test_id"
        assert creds.grant_type == "client_credentials"
        assert creds.access_token is None
    
    @patch('os.path.exists')
    @patch('configparser.ConfigParser.read')
    def test_config_reader_initialization(self, mock_read, mock_exists):
        """Test ConfigReader initialization."""
        mock_exists.return_value = True
        
        reader = ConfigReader("test_config.ini")
        
        mock_exists.assert_called_with("test_config.ini")
        mock_read.assert_called_with("test_config.ini")
    
    def test_config_reader_file_not_found(self):
        """Test ConfigReader with missing file."""
        with pytest.raises(FileNotFoundError):
            ConfigReader("nonexistent_config.ini")


class TestAgentTypes:
    """Test agent type enumerations and basic functionality."""
    
    def test_agent_type_values(self):
        """Test agent type enum values."""
        assert AgentType.SUPERVISOR.value == "supervisor"
        assert AgentType.RESEARCH.value == "research"
        assert AgentType.CODE.value == "code"
        assert AgentType.WRITING.value == "writing"
        assert AgentType.DATA.value == "data"
    
    def test_message_role_values(self):
        """Test message role enum values."""
        assert MessageRole.USER.value == "user"
        assert MessageRole.ASSISTANT.value == "assistant"
        assert MessageRole.SYSTEM.value == "system"


class TestEnvironmentSetup:
    """Test environment and configuration setup."""
    
    def test_required_directories_exist(self):
        """Test that required project directories exist."""
        required_dirs = [
            "agents",
            "core", 
            "utils",
            "config",
            "tests"
        ]
        
        for dir_name in required_dirs:
            assert os.path.exists(dir_name), f"Directory {dir_name} should exist"
    
    def test_required_files_exist(self):
        """Test that required project files exist."""
        required_files = [
            "requirements.txt",
            "README.md", 
            ".env.example",
            "main.py",
            "config/config.ini"
        ]
        
        for file_name in required_files:
            assert os.path.exists(file_name), f"File {file_name} should exist"
    
    def test_python_modules_importable(self):
        """Test that main modules can be imported."""
        try:
            from core.state import WorkflowState
            from config.config_reader import ConfigReader
            # Note: Other modules may fail due to missing dependencies
            # which is expected before pip install
        except ImportError as e:
            # Allow import errors for modules that depend on external packages
            if "pydantic" in str(e) or "langgraph" in str(e):
                pytest.skip(f"Skipping due to missing dependency: {e}")
            else:
                raise


if __name__ == "__main__":
    pytest.main([__file__])
