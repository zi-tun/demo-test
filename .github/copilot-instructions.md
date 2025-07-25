<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# GitHub MCP Server - Copilot Instructions

This is an MCP (Model Context Protocol) server project for GitHub integration. You can find more info and examples at https://modelcontextprotocol.io/llms-full.txt

## Project Structure
- Built with FastAPI and **FastMCP**
- Uses GitHub App authentication with PyGithub
- Implements webhook handling and GitHub Actions integration
- Provides tools for GitHub wiki operations

## Key Components
- **Authentication**: GitHub App with private key authentication
- **MCP Tools**: Exposed via **FastMCP** for repository, issue, PR, and wiki operations
- **Webhooks**: Real-time GitHub event processing
- **Actions**: GitHub Actions workflow integration

## Development Guidelines
- Follow async/await patterns for all GitHub API calls
- Use Pydantic models for request/response validation
- Implement proper error handling with GitHub API rate limits
- Use dependency injection for GitHub client configuration
- Add comprehensive logging for debugging

## Security Considerations
- Store private keys securely
- Validate webhook signatures
- Use environment variables for sensitive configuration
- Implement proper CORS settings for API endpoints

When working on this project, prioritize:
1. Type safety with Pydantic and mypy
2. Proper error handling for GitHub API interactions
3. Async programming patterns
4. Security best practices for webhook handling
