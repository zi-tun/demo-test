"""
Test native LangGraph visualization capabilities.
"""

def test_native_visualization():
    """Test LangGraph's built-in visualization features."""
    print("🎨 Testing Native LangGraph Visualization")
    print("=" * 45)
    
    try:
        from core.graph_builder import MultiAgentGraphBuilder
        
        # Build the graph
        builder = MultiAgentGraphBuilder()
        graph = builder.build_graph()
        
        print("✅ Graph built successfully")
        
        # Try native visualization
        try:
            result = builder.visualize_graph("langgraph_native.png")
            if result:
                print(f"✅ Native visualization saved as {result}")
            else:
                print("⚠️  Native visualization not available, using custom tools")
        except Exception as e:
            print(f"⚠️  Native visualization failed: {str(e)}")
        
        # Get graph info
        try:
            info = builder.get_graph_info()
            print(f"✅ Graph info: {len(info['nodes'])} nodes")
        except Exception as e:
            print(f"⚠️  Graph info failed: {str(e)}")
        
    except Exception as e:
        print(f"❌ Failed to build graph: {str(e)}")

if __name__ == "__main__":
    test_native_visualization()
