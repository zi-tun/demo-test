"""
Tool discovery and registry system for the multi-agent framework.
Provides centralized tool management and discovery capabilities.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Type, Callable
from dataclasses import dataclass
from enum import Enum
import inspect
import json


class ToolCategory(Enum):
    """Categories of tools available in the system."""
    RESEARCH = "research"
    CODE = "code"
    WRITING = "writing"
    DATA = "data"
    COMMUNICATION = "communication"
    FILE_SYSTEM = "file_system"
    WEB = "web"
    UTILITY = "utility"


@dataclass
class ToolMetadata:
    """Metadata describing a tool's capabilities and requirements."""
    name: str
    description: str
    category: ToolCategory
    parameters: Dict[str, Any]
    returns: Dict[str, Any]
    examples: List[str]
    requirements: List[str]
    agent_types: List[str]  # Which agents can use this tool
    version: str = "1.0.0"
    deprecated: bool = False


class BaseTool(ABC):
    """Abstract base class for all tools in the system."""
    
    def __init__(self, metadata: ToolMetadata):
        self.metadata = metadata
    
    @abstractmethod
    def execute(self, **kwargs) -> Any:
        """Execute the tool with given parameters."""
        pass
    
    @abstractmethod
    def validate_parameters(self, **kwargs) -> bool:
        """Validate that provided parameters are correct."""
        pass
    
    def get_help(self) -> str:
        """Get help text for this tool."""
        examples = "\n".join([f"  - {ex}" for ex in self.metadata.examples])
        return f"""
Tool: {self.metadata.name}
Description: {self.metadata.description}
Category: {self.metadata.category.value}
Parameters: {json.dumps(self.metadata.parameters, indent=2)}
Returns: {json.dumps(self.metadata.returns, indent=2)}
Examples:
{examples}
Requirements: {', '.join(self.metadata.requirements)}
Compatible Agents: {', '.join(self.metadata.agent_types)}
        """.strip()


class ToolRegistry:
    """Central registry for all available tools in the system."""
    
    def __init__(self):
        self.tools: Dict[str, BaseTool] = {}
        self.tools_by_category: Dict[ToolCategory, List[BaseTool]] = {}
        self.tools_by_agent: Dict[str, List[BaseTool]] = {}
        self._initialize_categories()
    
    def _initialize_categories(self):
        """Initialize category mappings."""
        for category in ToolCategory:
            self.tools_by_category[category] = []
        
        # Initialize common agent types
        for agent_type in ["supervisor", "research", "code", "writing", "data"]:
            self.tools_by_agent[agent_type] = []
    
    def register_tool(self, tool: BaseTool) -> None:
        """Register a new tool in the registry."""
        self.tools[tool.metadata.name] = tool
        
        # Add to category mapping
        if tool.metadata.category not in self.tools_by_category:
            self.tools_by_category[tool.metadata.category] = []
        self.tools_by_category[tool.metadata.category].append(tool)
        
        # Add to agent mapping
        for agent_type in tool.metadata.agent_types:
            if agent_type not in self.tools_by_agent:
                self.tools_by_agent[agent_type] = []
            self.tools_by_agent[agent_type].append(tool)
    
    def get_tool(self, name: str) -> Optional[BaseTool]:
        """Get a tool by name."""
        return self.tools.get(name)
    
    def get_tools_by_category(self, category: ToolCategory) -> List[BaseTool]:
        """Get all tools in a specific category."""
        return self.tools_by_category.get(category, [])
    
    def get_tools_for_agent(self, agent_type: str) -> List[BaseTool]:
        """Get all tools available to a specific agent type."""
        return self.tools_by_agent.get(agent_type, [])
    
    def search_tools(self, query: str, category: Optional[ToolCategory] = None) -> List[BaseTool]:
        """Search for tools by name or description."""
        results = []
        search_pool = (
            self.tools_by_category.get(category, []) 
            if category 
            else list(self.tools.values())
        )
        
        query_lower = query.lower()
        for tool in search_pool:
            if (query_lower in tool.metadata.name.lower() or 
                query_lower in tool.metadata.description.lower()):
                results.append(tool)
        
        return results
    
    def list_all_tools(self) -> List[BaseTool]:
        """Get a list of all registered tools."""
        return list(self.tools.values())
    
    def get_registry_summary(self) -> Dict[str, Any]:
        """Get a summary of the entire tool registry."""
        return {
            "total_tools": len(self.tools),
            "categories": {
                category.value: len(tools) 
                for category, tools in self.tools_by_category.items()
            },
            "agent_coverage": {
                agent: len(tools) 
                for agent, tools in self.tools_by_agent.items()
            },
            "tool_list": [
                {
                    "name": tool.metadata.name,
                    "category": tool.metadata.category.value,
                    "description": tool.metadata.description,
                    "agents": tool.metadata.agent_types
                }
                for tool in self.tools.values()
            ]
        }


class ToolDiscoveryService:
    """Service for dynamic tool discovery and recommendation."""
    
    def __init__(self, registry: ToolRegistry):
        self.registry = registry
    
    def discover_tools_for_task(self, task_description: str, agent_type: str) -> List[BaseTool]:
        """
        Discover relevant tools for a given task and agent type.
        
        Args:
            task_description: Description of the task to be performed
            agent_type: Type of agent requesting tools
            
        Returns:
            List of relevant tools
        """
        # Get tools available to this agent
        agent_tools = self.registry.get_tools_for_agent(agent_type)
        
        # Score tools based on relevance to task
        scored_tools = []
        task_lower = task_description.lower()
        
        for tool in agent_tools:
            score = self._calculate_relevance_score(tool, task_lower)
            if score > 0:
                scored_tools.append((tool, score))
        
        # Sort by relevance score (descending)
        scored_tools.sort(key=lambda x: x[1], reverse=True)
        
        return [tool for tool, score in scored_tools]
    
    def _calculate_relevance_score(self, tool: BaseTool, task_description: str) -> float:
        """Calculate how relevant a tool is to a task description."""
        score = 0.0
        
        # Check name relevance
        if any(word in tool.metadata.name.lower() for word in task_description.split()):
            score += 0.3
        
        # Check description relevance
        description_words = tool.metadata.description.lower().split()
        task_words = task_description.split()
        common_words = set(description_words) & set(task_words)
        score += len(common_words) * 0.1
        
        # Check examples relevance
        for example in tool.metadata.examples:
            if any(word in example.lower() for word in task_words):
                score += 0.2
        
        return score
    
    def recommend_tools_by_category(self, category: ToolCategory, limit: int = 5) -> List[BaseTool]:
        """Recommend top tools in a specific category."""
        tools = self.registry.get_tools_by_category(category)
        
        # Sort by some criteria (e.g., usage, rating, etc.)
        # For now, just return first N tools
        return tools[:limit]
    
    def get_tool_usage_suggestions(self, tool_name: str) -> Dict[str, Any]:
        """Get usage suggestions and examples for a specific tool."""
        tool = self.registry.get_tool(tool_name)
        if not tool:
            return {"error": f"Tool '{tool_name}' not found"}
        
        return {
            "tool": tool.metadata.name,
            "description": tool.metadata.description,
            "usage_examples": tool.metadata.examples,
            "parameters": tool.metadata.parameters,
            "compatible_agents": tool.metadata.agent_types,
            "requirements": tool.metadata.requirements,
            "help": tool.get_help()
        }


# Global tool registry instance
_global_registry = ToolRegistry()
_discovery_service = ToolDiscoveryService(_global_registry)


def get_tool_registry() -> ToolRegistry:
    """Get the global tool registry instance."""
    return _global_registry


def get_discovery_service() -> ToolDiscoveryService:
    """Get the global tool discovery service instance."""
    return _discovery_service


def register_tool(tool: BaseTool) -> None:
    """Register a tool in the global registry."""
    _global_registry.register_tool(tool)


def discover_tools(task_description: str, agent_type: str) -> List[BaseTool]:
    """Discover tools for a task (convenience function)."""
    return _discovery_service.discover_tools_for_task(task_description, agent_type)
