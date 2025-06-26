"""
Example tools to demonstrate the tool discovery system.
These tools showcase different categories and capabilities.
"""

import os
import json
import requests
from typing import Any, Dict, List, Optional
from datetime import datetime

from core.tool_discovery import BaseTool, ToolMetadata, ToolCategory, register_tool


class WebSearchTool(BaseTool):
    """Tool for searching the web (mock implementation)."""
    
    def __init__(self):
        metadata = ToolMetadata(
            name="web_search",
            description="Search the web for information on any topic",
            category=ToolCategory.RESEARCH,
            parameters={
                "query": {"type": "string", "required": True, "description": "Search query"},
                "limit": {"type": "integer", "default": 5, "description": "Number of results"}
            },
            returns={
                "results": {
                    "type": "array",
                    "items": {
                        "title": "string",
                        "url": "string", 
                        "snippet": "string"
                    }
                }
            },
            examples=[
                "web_search(query='python machine learning', limit=3)",
                "web_search(query='climate change latest research')"
            ],
            requirements=["internet_connection"],
            agent_types=["research", "supervisor"]
        )
        super().__init__(metadata)
    
    def validate_parameters(self, **kwargs) -> bool:
        return "query" in kwargs and isinstance(kwargs["query"], str)
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        if not self.validate_parameters(**kwargs):
            return {"error": "Invalid parameters"}
        
        query = kwargs["query"]
        limit = kwargs.get("limit", 5)
        
        # Mock search results
        return {
            "results": [
                {
                    "title": f"Search Result {i+1} for '{query}'",
                    "url": f"https://example.com/result-{i+1}",
                    "snippet": f"This is a mock search result snippet about {query}..."
                }
                for i in range(min(limit, 5))
            ],
            "query": query,
            "timestamp": datetime.now().isoformat()
        }


class CodeExecutorTool(BaseTool):
    """Tool for executing code safely (mock implementation)."""
    
    def __init__(self):
        metadata = ToolMetadata(
            name="code_executor",
            description="Execute code in a safe sandboxed environment",
            category=ToolCategory.CODE,
            parameters={
                "code": {"type": "string", "required": True, "description": "Code to execute"},
                "language": {"type": "string", "default": "python", "description": "Programming language"},
                "timeout": {"type": "integer", "default": 30, "description": "Execution timeout in seconds"}
            },
            returns={
                "output": {"type": "string", "description": "Code execution output"},
                "error": {"type": "string", "description": "Error message if execution failed"},
                "execution_time": {"type": "float", "description": "Time taken to execute"}
            },
            examples=[
                "code_executor(code='print(\"Hello World!\")', language='python')",
                "code_executor(code='console.log(\"Hello\");', language='javascript')"
            ],
            requirements=["sandboxed_environment", "runtime_engines"],
            agent_types=["code", "supervisor"]
        )
        super().__init__(metadata)
    
    def validate_parameters(self, **kwargs) -> bool:
        return "code" in kwargs and isinstance(kwargs["code"], str)
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        if not self.validate_parameters(**kwargs):
            return {"error": "Invalid parameters"}
        
        code = kwargs["code"]
        language = kwargs.get("language", "python")
        
        # Mock execution
        return {
            "output": f"Mock execution result for {language} code: {code[:50]}...",
            "error": None,
            "execution_time": 0.123,
            "language": language
        }


class FileManagerTool(BaseTool):
    """Tool for managing files and directories."""
    
    def __init__(self):
        metadata = ToolMetadata(
            name="file_manager",
            description="Read, write, and manage files and directories",
            category=ToolCategory.FILE_SYSTEM,
            parameters={
                "action": {"type": "string", "required": True, "description": "Action: read, write, list, delete"},
                "path": {"type": "string", "required": True, "description": "File or directory path"},
                "content": {"type": "string", "description": "Content for write operations"}
            },
            returns={
                "result": {"type": "any", "description": "Operation result"},
                "success": {"type": "boolean", "description": "Whether operation succeeded"}
            },
            examples=[
                "file_manager(action='read', path='/path/to/file.txt')",
                "file_manager(action='write', path='/path/to/file.txt', content='Hello World')",
                "file_manager(action='list', path='/path/to/directory')"
            ],
            requirements=["file_system_access"],
            agent_types=["code", "data", "supervisor"]
        )
        super().__init__(metadata)
    
    def validate_parameters(self, **kwargs) -> bool:
        required = "action" in kwargs and "path" in kwargs
        action = kwargs.get("action", "")
        if action == "write":
            required = required and "content" in kwargs
        return required
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        if not self.validate_parameters(**kwargs):
            return {"error": "Invalid parameters", "success": False}
        
        action = kwargs["action"]
        path = kwargs["path"]
        
        # Mock file operations
        if action == "read":
            return {
                "result": f"Mock content of file: {path}",
                "success": True
            }
        elif action == "write":
            content = kwargs["content"]
            return {
                "result": f"Successfully wrote {len(content)} characters to {path}",
                "success": True
            }
        elif action == "list":
            return {
                "result": [f"file_{i}.txt" for i in range(3)],
                "success": True
            }
        else:
            return {
                "error": f"Unknown action: {action}",
                "success": False
            }


class DataVisualizationTool(BaseTool):
    """Tool for creating data visualizations."""
    
    def __init__(self):
        metadata = ToolMetadata(
            name="data_visualization",
            description="Create charts and visualizations from data",
            category=ToolCategory.DATA,
            parameters={
                "data": {"type": "array", "required": True, "description": "Data to visualize"},
                "chart_type": {"type": "string", "default": "bar", "description": "Type of chart"},
                "title": {"type": "string", "description": "Chart title"},
                "x_axis": {"type": "string", "description": "X-axis label"},
                "y_axis": {"type": "string", "description": "Y-axis label"}
            },
            returns={
                "chart_url": {"type": "string", "description": "URL to generated chart"},
                "chart_data": {"type": "object", "description": "Chart configuration"}
            },
            examples=[
                "data_visualization(data=[1,2,3,4], chart_type='line', title='Growth')",
                "data_visualization(data=[{'x': 1, 'y': 2}], chart_type='scatter')"
            ],
            requirements=["plotting_library"],
            agent_types=["data", "supervisor"]
        )
        super().__init__(metadata)
    
    def validate_parameters(self, **kwargs) -> bool:
        return "data" in kwargs and isinstance(kwargs["data"], (list, dict))
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        if not self.validate_parameters(**kwargs):
            return {"error": "Invalid parameters"}
        
        data = kwargs["data"]
        chart_type = kwargs.get("chart_type", "bar")
        title = kwargs.get("title", "Data Visualization")
        
        return {
            "chart_url": f"https://charts.example.com/mock-chart-{hash(str(data))}",
            "chart_data": {
                "type": chart_type,
                "title": title,
                "data_points": len(data) if isinstance(data, list) else 1
            }
        }


class TextSummarizerTool(BaseTool):
    """Tool for summarizing text content."""
    
    def __init__(self):
        metadata = ToolMetadata(
            name="text_summarizer",
            description="Summarize long text content into key points",
            category=ToolCategory.WRITING,
            parameters={
                "text": {"type": "string", "required": True, "description": "Text to summarize"},
                "max_length": {"type": "integer", "default": 200, "description": "Maximum summary length"},
                "style": {"type": "string", "default": "bullet", "description": "Summary style: bullet, paragraph"}
            },
            returns={
                "summary": {"type": "string", "description": "Generated summary"},
                "key_points": {"type": "array", "description": "List of key points"},
                "word_count": {"type": "integer", "description": "Summary word count"}
            },
            examples=[
                "text_summarizer(text='Long article...', max_length=100)",
                "text_summarizer(text='Research paper...', style='paragraph')"
            ],
            requirements=["nlp_library"],
            agent_types=["writing", "research", "supervisor"]
        )
        super().__init__(metadata)
    
    def validate_parameters(self, **kwargs) -> bool:
        return "text" in kwargs and isinstance(kwargs["text"], str) and len(kwargs["text"]) > 0
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        if not self.validate_parameters(**kwargs):
            return {"error": "Invalid parameters"}
        
        text = kwargs["text"]
        max_length = kwargs.get("max_length", 200)
        style = kwargs.get("style", "bullet")
        
        # Mock summarization
        word_count = min(len(text.split()), max_length)
        
        if style == "bullet":
            summary = f"• Key point 1 from the text\n• Key point 2 from the text\n• Key point 3 from the text"
            key_points = ["Key point 1 from the text", "Key point 2 from the text", "Key point 3 from the text"]
        else:
            summary = f"This is a mock paragraph summary of the provided text. It contains the main ideas in a condensed format with approximately {word_count} words."
            key_points = ["Main idea 1", "Main idea 2", "Main idea 3"]
        
        return {
            "summary": summary,
            "key_points": key_points,
            "word_count": word_count
        }


# Register all tools
def register_example_tools():
    """Register all example tools in the global registry."""
    tools = [
        WebSearchTool(),
        CodeExecutorTool(),
        FileManagerTool(),
        DataVisualizationTool(),
        TextSummarizerTool()
    ]
    
    for tool in tools:
        register_tool(tool)
    
    return len(tools)


# Auto-register tools when module is imported
if __name__ != "__main__":
    register_example_tools()
