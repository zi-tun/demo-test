"""
DAG Visualization Tools for LangGraph Multi-Agent System
Provides multiple ways to visualize the workflow graph structure.
"""

import os
import json
from typing import Dict, List, Any, Optional
from datetime import datetime


class DAGVisualizer:
    """Visualizes the LangGraph DAG structure using various methods."""
    
    def __init__(self):
        self.graph_builder = None
    
    def load_graph(self):
        """Load the graph builder and build the graph."""
        from core.graph_builder import MultiAgentGraphBuilder
        
        self.graph_builder = MultiAgentGraphBuilder()
        self.graph_builder.build_graph()
        return self.graph_builder
    
    def print_ascii_dag(self):
        """Print an ASCII representation of the DAG."""
        print("🔄 LangGraph Multi-Agent DAG Structure")
        print("=" * 50)
        print()
        print("                    START")
        print("                      │")
        print("                      ▼")
        print("              ┌─────────────┐")
        print("              │ SUPERVISOR  │")
        print("              │   AGENT     │")
        print("              └─────┬───────┘")
        print("                    │")
        print("         ┌──────────┼──────────┐")
        print("         │          │          │")
        print("         ▼          ▼          ▼")
        print("   ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐")
        print("   │ RESEARCH │ │   CODE   │ │ WRITING  │ │   DATA   │")
        print("   │  AGENT   │ │  AGENT   │ │  AGENT   │ │  AGENT   │")
        print("   └─────┬────┘ └─────┬────┘ └─────┬────┘ └─────┬────┘")
        print("         │            │            │            │")
        print("         └──────────┬─┴──────────┬─┴────────────┘")
        print("                    │            │")
        print("                    ▼            ▼")
        print("                        END")
        print()
        print("🔀 Routing Logic:")
        print("   • Supervisor uses LLM-based intent classification")
        print("   • Routes to appropriate specialist agent")
        print("   • All agents terminate at END")
        print()
    
    def generate_mermaid_diagram(self) -> str:
        """Generate a Mermaid diagram representation."""
        mermaid = """
graph TD
    START([START]) --> SUPERVISOR[Supervisor Agent<br/>Intent Classification]
    
    SUPERVISOR -->|Research Intent| RESEARCH[Research Agent<br/>Web Search & Analysis]
    SUPERVISOR -->|Code Intent| CODE[Code Agent<br/>Programming & Scripts]
    SUPERVISOR -->|Writing Intent| WRITING[Writing Agent<br/>Content Creation]
    SUPERVISOR -->|Data Intent| DATA[Data Agent<br/>Analysis & Visualization]
    SUPERVISOR -->|General Intent| END_SUPER([END])
    
    RESEARCH --> END_R([END])
    CODE --> END_C([END])
    WRITING --> END_W([END])
    DATA --> END_D([END])
    
    %% Styling
    classDef supervisor fill:#ff9999,stroke:#333,stroke-width:3px
    classDef agents fill:#99ccff,stroke:#333,stroke-width:2px
    classDef endpoints fill:#99ff99,stroke:#333,stroke-width:2px
    
    class SUPERVISOR supervisor
    class RESEARCH,CODE,WRITING,DATA agents
    class END_SUPER,END_R,END_C,END_W,END_D endpoints
"""
        return mermaid.strip()
    
    def save_mermaid_html(self, filename: str = "dag_visualization.html"):
        """Save a complete HTML file with Mermaid visualization."""
        mermaid_diagram = self.generate_mermaid_diagram()
        
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LangGraph Multi-Agent DAG Visualization</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            background-color: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #333;
            text-align: center;
            margin-bottom: 30px;
        }}
        .info {{
            background-color: #e8f4f8;
            padding: 15px;
            border-left: 4px solid #2196F3;
            margin: 20px 0;
        }}
        .agent-details {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }}
        .agent-card {{
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #007bff;
        }}
        .agent-card h3 {{
            margin-top: 0;
            color: #007bff;
        }}
        #diagram {{
            background-color: white;
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🔄 LangGraph Multi-Agent DAG Visualization</h1>
        
        <div class="info">
            <strong>📊 Workflow Overview:</strong> This diagram shows the LangGraph workflow structure 
            for the multi-agent orchestration system. The supervisor agent uses LLM-based intent 
            classification to route user requests to specialized domain agents.
        </div>
        
        <div id="diagram">
            <div class="mermaid">
{mermaid_diagram}
            </div>
        </div>
        
        <div class="agent-details">
            <div class="agent-card">
                <h3>🎯 Supervisor Agent</h3>
                <p><strong>Role:</strong> Intent classification and routing</p>
                <p><strong>Capabilities:</strong> LLM-powered analysis, agent coordination, fallback handling</p>
            </div>
            
            <div class="agent-card">
                <h3>🔍 Research Agent</h3>
                <p><strong>Role:</strong> Information gathering and analysis</p>
                <p><strong>Tools:</strong> Web search, text summarization, fact checking</p>
            </div>
            
            <div class="agent-card">
                <h3>💻 Code Agent</h3>
                <p><strong>Role:</strong> Programming and script generation</p>
                <p><strong>Tools:</strong> Code execution, syntax validation, debugging</p>
            </div>
            
            <div class="agent-card">
                <h3>✍️ Writing Agent</h3>
                <p><strong>Role:</strong> Content creation and editing</p>
                <p><strong>Tools:</strong> Text generation, grammar checking, style optimization</p>
            </div>
            
            <div class="agent-card">
                <h3>📊 Data Agent</h3>
                <p><strong>Role:</strong> Data analysis and visualization</p>
                <p><strong>Tools:</strong> Chart generation, statistical analysis, data processing</p>
            </div>
        </div>
        
        <div class="info">
            <strong>Generated:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}<br>
            <strong>Provider:</strong> Cisco Enterprise OpenAI<br>
            <strong>System:</strong> LangGraph Multi-Agent Orchestration
        </div>
    </div>
    
    <script>
        mermaid.initialize({{ 
            startOnLoad: true,
            theme: 'default',
            flowchart: {{
                useMaxWidth: true,
                htmlLabels: true
            }}
        }});
    </script>
</body>
</html>
"""
        
        with open(filename, 'w') as f:
            f.write(html_content)
        
        return filename
    
    def print_graph_structure(self):
        """Print detailed graph structure information."""
        if not self.graph_builder:
            self.load_graph()
        
        print("📋 Detailed Graph Structure")
        print("=" * 40)
        
        # Nodes
        print("\n🔶 Nodes:")
        nodes = ["supervisor", "research", "code", "writing", "data"]
        for node in nodes:
            print(f"  • {node}")
        
        # Edges
        print("\n🔗 Edges:")
        print("  • START → supervisor (entry point)")
        print("  • supervisor → research (conditional)")
        print("  • supervisor → code (conditional)")
        print("  • supervisor → writing (conditional)")
        print("  • supervisor → data (conditional)")
        print("  • supervisor → END (conditional)")
        print("  • research → END")
        print("  • code → END")
        print("  • writing → END")
        print("  • data → END")
        
        # Routing conditions
        print("\n🎛️  Routing Conditions:")
        print("  • supervisor routes based on intent classification")
        print("  • research: information gathering, web search")
        print("  • code: programming tasks, scripts, debugging")
        print("  • writing: content creation, documentation")
        print("  • data: analysis, visualization, statistics")
        print("  • END: general conversation, coordination")
    
    def export_graph_json(self, filename: str = "dag_structure.json") -> str:
        """Export graph structure as JSON."""
        graph_data = {
            "metadata": {
                "title": "LangGraph Multi-Agent DAG",
                "description": "Workflow structure for multi-agent orchestration system",
                "created": datetime.now().isoformat(),
                "type": "langgraph_workflow"
            },
            "nodes": [
                {
                    "id": "supervisor",
                    "type": "agent",
                    "label": "Supervisor Agent",
                    "description": "Intent classification and routing",
                    "entry_point": True
                },
                {
                    "id": "research",
                    "type": "agent", 
                    "label": "Research Agent",
                    "description": "Information gathering and analysis"
                },
                {
                    "id": "code",
                    "type": "agent",
                    "label": "Code Agent", 
                    "description": "Programming and script generation"
                },
                {
                    "id": "writing",
                    "type": "agent",
                    "label": "Writing Agent",
                    "description": "Content creation and editing"
                },
                {
                    "id": "data",
                    "type": "agent",
                    "label": "Data Agent",
                    "description": "Data analysis and visualization"
                }
            ],
            "edges": [
                {"from": "START", "to": "supervisor", "type": "entry"},
                {"from": "supervisor", "to": "research", "type": "conditional", "condition": "research_intent"},
                {"from": "supervisor", "to": "code", "type": "conditional", "condition": "code_intent"},
                {"from": "supervisor", "to": "writing", "type": "conditional", "condition": "writing_intent"},
                {"from": "supervisor", "to": "data", "type": "conditional", "condition": "data_intent"},
                {"from": "supervisor", "to": "END", "type": "conditional", "condition": "general_intent"},
                {"from": "research", "to": "END", "type": "terminal"},
                {"from": "code", "to": "END", "type": "terminal"},
                {"from": "writing", "to": "END", "type": "terminal"},
                {"from": "data", "to": "END", "type": "terminal"}
            ],
            "routing_logic": {
                "supervisor": {
                    "method": "llm_intent_classification",
                    "routes": {
                        "research": ["research", "search", "information", "find", "lookup"],
                        "code": ["code", "program", "script", "function", "debug"],
                        "writing": ["write", "content", "document", "article", "edit"],
                        "data": ["data", "analyze", "chart", "visualize", "statistics"],
                        "END": ["general", "conversation", "hello", "help"]
                    }
                }
            }
        }
        
        with open(filename, 'w') as f:
            json.dump(graph_data, f, indent=2)
        
        return filename
    
    def visualize_all(self):
        """Generate all visualization formats."""
        print("🎨 Generating DAG Visualizations...")
        print("=" * 40)
        
        # ASCII representation
        self.print_ascii_dag()
        
        # Detailed structure
        self.print_graph_structure()
        
        # Generate files
        html_file = self.save_mermaid_html()
        json_file = self.export_graph_json()
        
        print(f"\n📁 Files Generated:")
        print(f"  • {html_file} - Interactive HTML visualization")
        print(f"  • {json_file} - JSON graph structure")
        
        print(f"\n🌐 To view the interactive diagram:")
        print(f"  open {html_file}")
        
        print(f"\n📊 Mermaid diagram code:")
        print("```mermaid")
        print(self.generate_mermaid_diagram())
        print("```")


def main():
    """Main visualization function."""
    visualizer = DAGVisualizer()
    visualizer.visualize_all()


if __name__ == "__main__":
    main()
