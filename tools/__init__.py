"""Tools package initialization."""

from .example_tools import register_example_tools

# Auto-register example tools
register_example_tools()

__all__ = ["register_example_tools"]
