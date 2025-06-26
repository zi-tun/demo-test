"""
LangGraph workflow builder for multi-agent orchestration.
Creates and manages the graph structure with conditional routing between agents.
"""

from typing import Any, Dict

# Note: Import errors will resolve after installing dependencies
try:
    from langgraph.graph import StateGraph, END
    from langgraph.checkpoint.memory import MemorySaver
except ImportError:
    # Will be resolved after pip install
    StateGraph = None
    END = None
    MemorySaver = None

from core.state import WorkflowState, AgentType


class MultiAgentGraphBuilder:
    """Builds and manages the LangGraph workflow for multi-agent orchestration."""
    
    def __init__(self):
        """Initialize the graph builder with agents and state management."""
        if StateGraph is None:
            raise ImportError("langgraph package not installed. Run: pip install langgraph")
        
        # Import agents here to avoid circular imports
        from agents.supervisor import SupervisorAgent
        from agents.research_agent import ResearchAgent
        from agents.code_agent import CodeAgent
        from agents.writing_agent import WritingAgent
        from agents.data_agent import DataAgent
        
        self.supervisor = SupervisorAgent()
        self.research_agent = ResearchAgent()
        self.code_agent = CodeAgent()
        self.writing_agent = WritingAgent()
        self.data_agent = DataAgent()
        
        # Register agents with supervisor
        self.supervisor.register_agent(self.research_agent)
        self.supervisor.register_agent(self.code_agent)
        self.supervisor.register_agent(self.writing_agent)
        self.supervisor.register_agent(self.data_agent)
        
        self.graph = None
        self.memory = MemorySaver() if MemorySaver else None
    
    def build_graph(self) -> Any:
        """
        Build the LangGraph workflow with conditional routing.
        
        Returns:
            Compiled LangGraph workflow
        """
        # Create the state graph
        workflow = StateGraph(WorkflowState)
        
        # Add agent nodes
        workflow.add_node("supervisor", self._supervisor_node)
        workflow.add_node("research", self._research_node)
        workflow.add_node("code", self._code_node)
        workflow.add_node("writing", self._writing_node)
        workflow.add_node("data", self._data_node)
        
        # Set entry point
        workflow.set_entry_point("supervisor")
        
        # Add conditional routing from supervisor
        workflow.add_conditional_edges(
            "supervisor",
            self._route_from_supervisor,
            {
                AgentType.SUPERVISOR.value: END,
                AgentType.RESEARCH.value: "research",
                AgentType.CODE.value: "code",
                AgentType.WRITING.value: "writing",
                AgentType.DATA.value: "data",
                "END": END
            }
        )
        
        # All specialized agents return to END
        workflow.add_edge("research", END)
        workflow.add_edge("code", END)
        workflow.add_edge("writing", END)
        workflow.add_edge("data", END)
        
        # Compile the graph
        self.graph = workflow.compile(checkpointer=self.memory)
        return self.graph
    
    def _supervisor_node(self, state: WorkflowState) -> Dict[str, Any]:
        """Process state through the supervisor agent."""
        try:
            updated_state = self.supervisor.process_request(state)
            return updated_state.dict()
        except Exception as e:
            state.record_error(f"Supervisor node error: {str(e)}")
            return state.dict()
    
    def _research_node(self, state: WorkflowState) -> Dict[str, Any]:
        """Process state through the research agent."""
        try:
            updated_state = self.research_agent.process_request(state)
            return updated_state.dict()
        except Exception as e:
            state.record_error(f"Research node error: {str(e)}")
            return state.dict()
    
    def _code_node(self, state: WorkflowState) -> Dict[str, Any]:
        """Process state through the code agent."""
        try:
            updated_state = self.code_agent.process_request(state)
            return updated_state.dict()
        except Exception as e:
            state.record_error(f"Code node error: {str(e)}")
            return state.dict()
    
    def _writing_node(self, state: WorkflowState) -> Dict[str, Any]:
        """Process state through the writing agent."""
        try:
            updated_state = self.writing_agent.process_request(state)
            return updated_state.dict()
        except Exception as e:
            state.record_error(f"Writing node error: {str(e)}")
            return state.dict()
    
    def _data_node(self, state: WorkflowState) -> Dict[str, Any]:
        """Process state through the data agent."""
        try:
            updated_state = self.data_agent.process_request(state)
            return updated_state.dict()
        except Exception as e:
            state.record_error(f"Data node error: {str(e)}")
            return state.dict()
    
    def _route_from_supervisor(self, state: WorkflowState) -> str:
        """
        Determine routing from supervisor based on state.
        
        Args:
            state: Current workflow state
            
        Returns:
            Next node identifier
        """
        # If supervisor handled directly, end workflow
        if state.current_agent == AgentType.SUPERVISOR and state.final_response:
            return "END"
        
        # Route to the determined agent
        if state.current_agent == AgentType.RESEARCH:
            return AgentType.RESEARCH.value
        elif state.current_agent == AgentType.CODE:
            return AgentType.CODE.value
        elif state.current_agent == AgentType.WRITING:
            return AgentType.WRITING.value
        elif state.current_agent == AgentType.DATA:
            return AgentType.DATA.value
        else:
            # Fallback to supervisor handling
            return AgentType.SUPERVISOR.value
    
    def process_user_input(self, user_input: str, config: Dict[str, Any] = None) -> WorkflowState:
        """
        Process user input through the multi-agent workflow.
        
        Args:
            user_input: User's input message
            config: Optional configuration for the workflow
            
        Returns:
            Final workflow state with response
        """
        if self.graph is None:
            self.build_graph()
        
        # Initialize state for new input
        initial_state = WorkflowState()
        initial_state.reset_for_new_input(user_input)
        
        try:
            # Run the workflow
            config = config or {"configurable": {"thread_id": "default"}}
            result = self.graph.invoke(initial_state.dict(), config)
            
            # Convert result back to WorkflowState
            final_state = WorkflowState(**result)
            
            # Ensure we have a final response
            if not final_state.final_response:
                final_state.final_response = "I apologize, but I wasn't able to generate a proper response. Please try rephrasing your request."
                final_state.record_error("No final response generated")
            
            return final_state
            
        except Exception as e:
            # Handle workflow execution errors
            initial_state.record_error(f"Workflow execution error: {str(e)}")
            initial_state.final_response = (
                "I apologize, but I encountered a technical issue while processing your request. "
                "Please try again or rephrase your question."
            )
            return initial_state
    
    def get_workflow_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the workflow configuration.
        
        Returns:
            Workflow summary information
        """
        return {
            "agents": {
                "supervisor": {
                    "name": self.supervisor.name,
                    "description": self.supervisor.description,
                    "capabilities": self.supervisor.get_capabilities()
                },
                "research": {
                    "name": self.research_agent.name,
                    "description": self.research_agent.description,
                    "capabilities": self.research_agent.get_capabilities()
                },
                "code": {
                    "name": self.code_agent.name,
                    "description": self.code_agent.description,
                    "capabilities": self.code_agent.get_capabilities()
                },
                "writing": {
                    "name": self.writing_agent.name,
                    "description": self.writing_agent.description,
                    "capabilities": self.writing_agent.get_capabilities()
                },
                "data": {
                    "name": self.data_agent.name,
                    "description": self.data_agent.description,
                    "capabilities": self.data_agent.get_capabilities()
                }
            },
            "routing": {
                "entry_point": "supervisor",
                "conditional_routing": True,
                "fallback_enabled": True,
                "memory_enabled": self.memory is not None
            }
        }
    
    def reset_memory(self) -> None:
        """Reset the workflow memory/checkpointer."""
        if self.memory:
            self.memory = MemorySaver()
    
    def get_agent_by_type(self, agent_type: AgentType) -> Any:
        """Get agent instance by type."""
        agent_map = {
            AgentType.SUPERVISOR: self.supervisor,
            AgentType.RESEARCH: self.research_agent,
            AgentType.CODE: self.code_agent,
            AgentType.WRITING: self.writing_agent,
            AgentType.DATA: self.data_agent
        }
        return agent_map.get(agent_type)
    
    def visualize_graph(self, filename: str = "langgraph_dag.png"):
        """
        Generate a visual representation of the graph using LangGraph's built-in visualization.
        
        Args:
            filename: Output filename for the visualization
        """
        if not self.graph:
            self.build_graph()
        
        try:
            # Try to use LangGraph's built-in visualization
            from langgraph.graph import draw_png, draw_mermaid
            
            # Generate PNG if possible
            try:
                png_data = draw_png(self.graph)
                with open(filename, 'wb') as f:
                    f.write(png_data)
                print(f"✅ Graph visualization saved as {filename}")
                return filename
            except Exception as e:
                print(f"⚠️  PNG generation failed: {str(e)}")
            
            # Fallback to Mermaid
            try:
                mermaid_code = draw_mermaid(self.graph)
                mermaid_filename = filename.replace('.png', '.mmd')
                with open(mermaid_filename, 'w') as f:
                    f.write(mermaid_code)
                print(f"✅ Mermaid diagram saved as {mermaid_filename}")
                return mermaid_filename
            except Exception as e:
                print(f"⚠️  Mermaid generation failed: {str(e)}")
                
        except ImportError:
            print("⚠️  LangGraph visualization not available. Using custom visualization instead.")
        
        return None
    
    def get_graph_info(self) -> Dict[str, Any]:
        """Get detailed information about the graph structure."""
        if not self.graph:
            self.build_graph()
        
        return {
            "nodes": ["supervisor", "research", "code", "writing", "data"],
            "entry_point": "supervisor",
            "routing_conditions": {
                "supervisor": {
                    "research": "Research and information gathering tasks",
                    "code": "Programming and coding tasks", 
                    "writing": "Content creation and writing tasks",
                    "data": "Data analysis and visualization tasks",
                    "END": "General conversation and coordination"
                }
            },
            "agent_capabilities": self.get_workflow_summary()
        }
