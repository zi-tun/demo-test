"""
Tool discovery CLI for exploring available tools in the system.
Provides commands to list, search, and get information about tools.
"""

import argparse
import json
from typing import Optional

from core.tool_discovery import get_tool_registry, get_discovery_service, ToolCategory
from tools import register_example_tools  # This will auto-register tools


def list_tools(category: Optional[str] = None, agent: Optional[str] = None):
    """List all available tools, optionally filtered by category or agent."""
    registry = get_tool_registry()
    
    if category:
        try:
            cat = ToolCategory(category.lower())
            tools = registry.get_tools_by_category(cat)
            print(f"\n🔧 Tools in category '{category}':")
        except ValueError:
            print(f"❌ Invalid category: {category}")
            print(f"Valid categories: {[c.value for c in ToolCategory]}")
            return
    elif agent:
        tools = registry.get_tools_for_agent(agent.lower())
        print(f"\n🤖 Tools available to '{agent}' agent:")
    else:
        tools = registry.list_all_tools()
        print(f"\n🔧 All available tools ({len(tools)} total):")
    
    if not tools:
        print("No tools found.")
        return
    
    for i, tool in enumerate(tools, 1):
        agents = ", ".join(tool.metadata.agent_types)
        print(f"{i:2d}. {tool.metadata.name}")
        print(f"    Category: {tool.metadata.category.value}")
        print(f"    Description: {tool.metadata.description}")
        print(f"    Compatible with: {agents}")
        print()


def search_tools(query: str, category: Optional[str] = None):
    """Search for tools by name or description."""
    registry = get_tool_registry()
    
    cat = None
    if category:
        try:
            cat = ToolCategory(category.lower())
        except ValueError:
            print(f"❌ Invalid category: {category}")
            return
    
    tools = registry.search_tools(query, cat)
    
    if category:
        print(f"\n🔍 Search results for '{query}' in category '{category}':")
    else:
        print(f"\n🔍 Search results for '{query}':")
    
    if not tools:
        print("No matching tools found.")
        return
    
    for i, tool in enumerate(tools, 1):
        print(f"{i}. {tool.metadata.name} - {tool.metadata.description}")


def show_tool_details(tool_name: str):
    """Show detailed information about a specific tool."""
    registry = get_tool_registry()
    tool = registry.get_tool(tool_name)
    
    if not tool:
        print(f"❌ Tool '{tool_name}' not found.")
        similar = registry.search_tools(tool_name)
        if similar:
            print(f"Did you mean one of these?")
            for t in similar[:3]:
                print(f"  - {t.metadata.name}")
        return
    
    print(f"\n📋 Tool Details: {tool.metadata.name}")
    print("=" * 50)
    print(f"Description: {tool.metadata.description}")
    print(f"Category: {tool.metadata.category.value}")
    print(f"Version: {tool.metadata.version}")
    print(f"Compatible agents: {', '.join(tool.metadata.agent_types)}")
    
    if tool.metadata.requirements:
        print(f"Requirements: {', '.join(tool.metadata.requirements)}")
    
    print("\nParameters:")
    for param, info in tool.metadata.parameters.items():
        required = " (required)" if info.get("required", False) else ""
        default = f" [default: {info.get('default')}]" if 'default' in info else ""
        print(f"  {param}: {info.get('type', 'unknown')}{required}{default}")
        if 'description' in info:
            print(f"    {info['description']}")
    
    print("\nReturns:")
    for field, info in tool.metadata.returns.items():
        print(f"  {field}: {info.get('type', 'unknown')}")
        if 'description' in info:
            print(f"    {info['description']}")
    
    if tool.metadata.examples:
        print("\nExamples:")
        for example in tool.metadata.examples:
            print(f"  {example}")


def discover_tools_for_task(task: str, agent: str):
    """Discover relevant tools for a specific task and agent."""
    discovery = get_discovery_service()
    tools = discovery.discover_tools_for_task(task, agent)
    
    print(f"\n🎯 Tools recommended for '{task}' (agent: {agent}):")
    
    if not tools:
        print("No relevant tools found for this task.")
        return
    
    for i, tool in enumerate(tools, 1):
        print(f"{i}. {tool.metadata.name}")
        print(f"   {tool.metadata.description}")
        print(f"   Category: {tool.metadata.category.value}")
        print()


def show_registry_summary():
    """Show a summary of the entire tool registry."""
    registry = get_tool_registry()
    summary = registry.get_registry_summary()
    
    print("\n📊 Tool Registry Summary")
    print("=" * 30)
    print(f"Total tools: {summary['total_tools']}")
    
    print("\nBy category:")
    for category, count in summary['categories'].items():
        print(f"  {category}: {count} tools")
    
    print("\nBy agent type:")
    for agent, count in summary['agent_coverage'].items():
        print(f"  {agent}: {count} tools")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="Tool Discovery CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List available tools")
    list_parser.add_argument("--category", "-c", help="Filter by category")
    list_parser.add_argument("--agent", "-a", help="Filter by agent type")
    
    # Search command
    search_parser = subparsers.add_parser("search", help="Search for tools")
    search_parser.add_argument("query", help="Search query")
    search_parser.add_argument("--category", "-c", help="Search within category")
    
    # Show command
    show_parser = subparsers.add_parser("show", help="Show tool details")
    show_parser.add_argument("tool_name", help="Name of the tool to show")
    
    # Discover command
    discover_parser = subparsers.add_parser("discover", help="Discover tools for a task")
    discover_parser.add_argument("task", help="Task description")
    discover_parser.add_argument("agent", help="Agent type")
    
    # Summary command
    subparsers.add_parser("summary", help="Show registry summary")
    
    args = parser.parse_args()
    
    if args.command == "list":
        list_tools(args.category, args.agent)
    elif args.command == "search":
        search_tools(args.query, args.category)
    elif args.command == "show":
        show_tool_details(args.tool_name)
    elif args.command == "discover":
        discover_tools_for_task(args.task, args.agent)
    elif args.command == "summary":
        show_registry_summary()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
