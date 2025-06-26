"""
Execution trace visualizer for the multi-agent system.
Shows the actual path taken through the DAG for specific queries.
"""

import json
from datetime import datetime
from typing import List, Dict, Any


class ExecutionTracer:
    """Traces and visualizes execution paths through the DAG."""
    
    def __init__(self):
        self.execution_log = []
    
    def trace_query_execution(self, query: str, save_trace: bool = True) -> Dict[str, Any]:
        """
        Execute a query and trace the path through the DAG.
        
        Args:
            query: The query to execute and trace
            save_trace: Whether to save the trace to a file
            
        Returns:
            Execution trace information
        """
        print(f"🔍 Tracing execution for: '{query}'")
        print("=" * 50)
        
        # Import here to avoid circular imports
        from core.graph_builder import MultiAgentGraphBuilder
        from core.state import WorkflowState
        
        # Build the graph
        builder = MultiAgentGraphBuilder()
        builder.build_graph()
        
        # Create initial state
        initial_state = WorkflowState(current_user_input=query)
        
        # Trace execution
        trace_data = {
            "query": query,
            "timestamp": datetime.now().isoformat(),
            "execution_path": [],
            "agent_decisions": [],
            "final_response": "",
            "total_time": 0
        }
        
        start_time = datetime.now()
        
        try:
            # Process through supervisor first
            print("1. 🎯 SUPERVISOR AGENT")
            print("   └─ Analyzing query intent...")
            
            supervisor_state = builder.supervisor.process_request(initial_state)
            
            # Record supervisor decision
            decision = {
                "agent": "supervisor",
                "intent": supervisor_state.detected_intent,
                "confidence": supervisor_state.intent_confidence,
                "target_agent": supervisor_state.current_agent.value,
                "reasoning": f"Classified as {supervisor_state.detected_intent} with {supervisor_state.intent_confidence:.2f} confidence"
            }
            trace_data["agent_decisions"].append(decision)
            trace_data["execution_path"].append("supervisor")
            
            print(f"   └─ Intent: {supervisor_state.detected_intent}")
            print(f"   └─ Confidence: {supervisor_state.intent_confidence:.2f}")
            print(f"   └─ Routing to: {supervisor_state.current_agent.value}")
            
            # Execute target agent if not supervisor
            if supervisor_state.current_agent.value != "supervisor":
                target_agent_name = supervisor_state.current_agent.value
                print(f"\n2. 🤖 {target_agent_name.upper()} AGENT")
                print("   └─ Processing specialized request...")
                
                # Get the appropriate agent
                target_agent = getattr(builder, f"{target_agent_name}_agent")
                final_state = target_agent.process_request(supervisor_state)
                
                trace_data["execution_path"].append(target_agent_name)
                trace_data["final_response"] = final_state.final_response
                
                print(f"   └─ Generated response: {final_state.final_response[:100]}...")
            else:
                final_state = supervisor_state
                trace_data["final_response"] = final_state.final_response
                print(f"   └─ Handled directly: {final_state.final_response[:100]}...")
            
            end_time = datetime.now()
            trace_data["total_time"] = (end_time - start_time).total_seconds()
            trace_data["execution_path"].append("END")
            
            print(f"\n✅ Execution completed in {trace_data['total_time']:.3f} seconds")
            print(f"📊 Path: {' → '.join(trace_data['execution_path'])}")
            
        except Exception as e:
            print(f"❌ Execution failed: {str(e)}")
            trace_data["error"] = str(e)
        
        # Save trace if requested
        if save_trace:
            self.execution_log.append(trace_data)
            filename = f"execution_trace_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w') as f:
                json.dump(trace_data, f, indent=2)
            print(f"💾 Trace saved to {filename}")
        
        return trace_data
    
    def visualize_execution_path(self, trace_data: Dict[str, Any]):
        """Visualize the execution path as ASCII art."""
        path = trace_data["execution_path"]
        query = trace_data["query"]
        
        print(f"\n🛤️  Execution Path for: '{query}'")
        print("=" * 60)
        
        # Draw the path
        for i, node in enumerate(path):
            if i == 0:
                print(f"START")
                print("  │")
                print("  ▼")
            
            if node == "supervisor":
                print("┌─────────────┐")
                print("│ SUPERVISOR  │")
                print("│   AGENT     │")
                print("└─────┬───────┘")
                
                if len(path) > 2:  # Has target agent
                    print("      │")
                    print("      ▼")
            
            elif node in ["research", "code", "writing", "data"]:
                print(f"┌─────────────┐")
                print(f"│ {node.upper():^11} │")
                print(f"│   AGENT     │")
                print(f"└─────┬───────┘")
                print("      │")
                print("      ▼")
            
            elif node == "END":
                print("    END")
        
        # Show decision details
        if "agent_decisions" in trace_data:
            print(f"\n🧠 Decision Details:")
            for decision in trace_data["agent_decisions"]:
                print(f"   • {decision['agent']}: {decision['reasoning']}")
    
    def generate_execution_report(self, queries: List[str]) -> str:
        """Generate a comprehensive execution report for multiple queries."""
        print("📈 Generating Execution Report")
        print("=" * 40)
        
        report_data = {
            "metadata": {
                "generated": datetime.now().isoformat(),
                "total_queries": len(queries),
                "system": "LangGraph Multi-Agent"
            },
            "executions": [],
            "statistics": {
                "agent_usage": {},
                "intent_distribution": {},
                "average_execution_time": 0
            }
        }
        
        total_time = 0
        agent_counts = {}
        intent_counts = {}
        
        for i, query in enumerate(queries, 1):
            print(f"\n📝 Testing Query {i}/{len(queries)}: {query[:50]}...")
            trace = self.trace_query_execution(query, save_trace=False)
            report_data["executions"].append(trace)
            
            # Update statistics
            total_time += trace.get("total_time", 0)
            
            for decision in trace.get("agent_decisions", []):
                agent = decision.get("target_agent", "unknown")
                intent = decision.get("intent", "unknown")
                
                agent_counts[agent] = agent_counts.get(agent, 0) + 1
                intent_counts[intent] = intent_counts.get(intent, 0) + 1
        
        # Calculate statistics
        report_data["statistics"]["agent_usage"] = agent_counts
        report_data["statistics"]["intent_distribution"] = intent_counts
        report_data["statistics"]["average_execution_time"] = total_time / len(queries) if queries else 0
        
        # Save report
        filename = f"execution_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        # Print summary
        print(f"\n📊 Execution Summary:")
        print(f"   • Total queries: {len(queries)}")
        print(f"   • Average time: {report_data['statistics']['average_execution_time']:.3f}s")
        print(f"   • Agent usage: {dict(agent_counts)}")
        print(f"   • Intent distribution: {dict(intent_counts)}")
        print(f"   • Report saved: {filename}")
        
        return filename


def main():
    """Main function for interactive DAG tracing."""
    tracer = ExecutionTracer()
    
    print("🔍 LangGraph DAG Execution Tracer")
    print("=" * 40)
    print("This tool traces the execution path through the multi-agent DAG.")
    print("Enter queries to see how they're routed through the system.\n")
    
    # Sample queries for testing
    sample_queries = [
        "Can you help me write Python code for a web scraper?",
        "What's the latest research on machine learning?", 
        "Please write a blog post about artificial intelligence",
        "Analyze this sales data and create a chart",
        "Hello, how are you today?"
    ]
    
    print("📝 Sample Queries:")
    for i, query in enumerate(sample_queries, 1):
        print(f"   {i}. {query}")
    
    print(f"\n🎯 Choose an option:")
    print("   1. Trace a sample query")
    print("   2. Enter your own query") 
    print("   3. Run full test suite")
    print("   4. Exit")
    
    choice = input("\nEnter choice (1-4): ").strip()
    
    if choice == "1":
        print("\nChoose a sample query (1-5):")
        query_num = input("Query number: ").strip()
        try:
            query_idx = int(query_num) - 1
            if 0 <= query_idx < len(sample_queries):
                query = sample_queries[query_idx]
                trace = tracer.trace_query_execution(query)
                tracer.visualize_execution_path(trace)
            else:
                print("Invalid query number")
        except ValueError:
            print("Please enter a valid number")
    
    elif choice == "2":
        query = input("\nEnter your query: ").strip()
        if query:
            trace = tracer.trace_query_execution(query)
            tracer.visualize_execution_path(trace)
    
    elif choice == "3":
        print("\n🧪 Running full test suite...")
        tracer.generate_execution_report(sample_queries)
    
    else:
        print("Goodbye!")


if __name__ == "__main__":
    main()
