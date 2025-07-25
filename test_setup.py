#!/usr/bin/env python3
"""Test script for GitHub MCP Server."""

import asyncio
import os
from github_mcp_server.auth import GitHubAppAuth
from github_mcp_server.config import get_config


async def test_github_auth():
    """Test GitHub authentication."""
    try:
        config = get_config()
        auth = GitHubAppAuth()
        jwt_token = auth.create_jwt_token()
        print(f"✅ GitHub App authentication successful")
        print(f"   App ID: {config.github_app_id}")
        print(f"   Private key path: {config.github_private_key_path}")
        print(f"   JWT token generated: {jwt_token[:20]}...")
        
        # Test getting GitHub client
        github = auth.get_github_client()
        app = github.get_app()
        print(f"   App name: {app.name}")
        print(f"   App owner: {app.owner.login}")
        
        return True
    except Exception as e:
        print(f"❌ GitHub App authentication failed: {str(e)}")
        return False


async def test_mcp_server():
    """Test MCP server functionality."""
    try:
        config = get_config()
        auth = GitHubAppAuth()
        
        print(f"✅ MCP server configuration loaded successfully")
        print(f"   GitHub App ID: {config.github_app_id}")
        print(f"   Server host: {config.server_host}")
        print(f"   Server port: {config.server_port}")
        print(f"   Using FastAPI-MCP integration")
        
        # Test GitHub authentication
        jwt_token = auth.create_jwt_token()
        print(f"   JWT token generated: {jwt_token[:20]}...")
        
        return True
    except Exception as e:
        print(f"❌ MCP server configuration failed: {str(e)}")
        return False


async def main():
    """Run all tests."""
    print("🧪 Testing GitHub MCP Server setup...\n")
    
    auth_success = await test_github_auth()
    print()
    
    mcp_success = await test_mcp_server()
    print()
    
    if auth_success and mcp_success:
        print("🎉 All tests passed! Your GitHub MCP Server is ready to use.")
        print("\nNext steps:")
        print("1. Set up your webhook secret in .env file")
        print("2. Configure your GitHub App webhook URL")
        print("3. Install the GitHub App on your repositories")
        print("4. Start the server with: uvicorn src.github_mcp_server.main:app --reload")
    else:
        print("❌ Some tests failed. Please check your configuration.")


if __name__ == "__main__":
    asyncio.run(main())
