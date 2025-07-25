"""GitHub MCP Server main application."""

import logging
from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi_mcp import FastApiMCP

from github_mcp_server.config import get_config
from github_mcp_server.auth import GitHubAppAuth
from github_mcp_server.webhooks import router as webhook_router
from github_mcp_server.actions import router as actions_router
from github_mcp_server.tools import (
    create_repository,
    get_repository_info,
    create_issue,
    update_issue,
    create_pull_request,
    merge_pull_request,
    create_wiki_page,
    update_wiki_page,
    delete_wiki_page,
    trigger_workflow,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables
auth: GitHubAppAuth = None


# Pydantic models for GitHub operations
class CreateRepoRequest(BaseModel):
    owner: str
    name: str
    description: str = ""
    private: bool = False
    installation_id: Optional[int] = None


class GetRepoRequest(BaseModel):
    owner: str
    name: str
    installation_id: Optional[int] = None


class CreateIssueRequest(BaseModel):
    owner: str
    repo: str
    title: str
    body: str = ""
    assignee: Optional[str] = None
    installation_id: Optional[int] = None


class UpdateIssueRequest(BaseModel):
    owner: str
    repo: str
    issue_number: int
    title: Optional[str] = None
    body: Optional[str] = None
    state: Optional[str] = None
    installation_id: Optional[int] = None


class CreatePRRequest(BaseModel):
    owner: str
    repo: str
    title: str
    head: str
    base: str
    body: str = ""
    installation_id: Optional[int] = None


class MergePRRequest(BaseModel):
    owner: str
    repo: str
    pull_number: int
    commit_title: Optional[str] = None
    commit_message: Optional[str] = None
    merge_method: str = "merge"
    installation_id: Optional[int] = None


class WikiPageRequest(BaseModel):
    owner: str
    repo: str
    title: str
    content: str
    installation_id: Optional[int] = None


class DeleteWikiPageRequest(BaseModel):
    owner: str
    repo: str
    title: str
    installation_id: Optional[int] = None


class TriggerWorkflowRequest(BaseModel):
    owner: str
    repo: str
    workflow_id: str
    ref: str = "main"
    inputs: Optional[Dict[str, Any]] = None
    installation_id: Optional[int] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    global auth
    
    try:
        # Load configuration
        config = get_config()
        logger.info(f"Loading configuration from config file")
        logger.info(f"GitHub App ID: {config.github_app_id}")
        
        # Initialize GitHub App authentication
        auth = GitHubAppAuth()
        logger.info("GitHub App authentication initialized")
        
        yield
        
    except Exception as e:
        logger.error(f"Failed to initialize application: {e}")
        raise


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="GitHub MCP Server",
        description="Model Context Protocol server for GitHub integration",
        version="0.1.0",
        lifespan=lifespan,
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include routers
    app.include_router(webhook_router, prefix="/webhooks")
    app.include_router(actions_router, prefix="/actions")
    
    # GitHub MCP Tools as FastAPI endpoints
    @app.post("/tools/create_repo", operation_id="create_repo", summary="Create a new GitHub repository")
    async def create_repo_endpoint(request: CreateRepoRequest) -> Dict[str, Any]:
        """Creates a new GitHub repository."""
        return await create_repository(
            auth, request.owner, request.name, request.description, 
            request.private, request.installation_id
        )
    
    @app.post("/tools/get_repo_info", operation_id="get_repo_info", summary="Get GitHub repository information")
    async def get_repo_info_endpoint(request: GetRepoRequest) -> Dict[str, Any]:
        """Gets information about a GitHub repository."""
        return await get_repository_info(auth, request.owner, request.name, request.installation_id)
    
    @app.post("/tools/create_issue", operation_id="create_issue", summary="Create a new GitHub issue")
    async def create_issue_endpoint(request: CreateIssueRequest) -> Dict[str, Any]:
        """Creates a new issue in a GitHub repository."""
        return await create_issue(
            auth, request.owner, request.repo, request.title, 
            request.body, request.assignee, request.installation_id
        )
    
    @app.post("/tools/update_issue", operation_id="update_issue", summary="Update a GitHub issue")
    async def update_issue_endpoint(request: UpdateIssueRequest) -> Dict[str, Any]:
        """Updates an existing GitHub issue."""
        return await update_issue(
            auth, request.owner, request.repo, request.issue_number,
            request.title, request.body, request.state, request.installation_id
        )
    
    @app.post("/tools/create_pull_request", operation_id="create_pull_request", summary="Create a new pull request")
    async def create_pr_endpoint(request: CreatePRRequest) -> Dict[str, Any]:
        """Creates a new pull request in a GitHub repository."""
        return await create_pull_request(
            auth, request.owner, request.repo, request.title,
            request.head, request.base, request.body, request.installation_id
        )
    
    @app.post("/tools/merge_pull_request", operation_id="merge_pull_request", summary="Merge a pull request")
    async def merge_pr_endpoint(request: MergePRRequest) -> Dict[str, Any]:
        """Merges a pull request in a GitHub repository."""
        return await merge_pull_request(
            auth, request.owner, request.repo, request.pull_number,
            request.commit_title, request.commit_message, request.merge_method, request.installation_id
        )
    
    @app.post("/tools/create_wiki_page", operation_id="create_wiki_page", summary="Create a wiki page")
    async def create_wiki_endpoint(request: WikiPageRequest) -> Dict[str, Any]:
        """Creates a new wiki page in a GitHub repository."""
        return await create_wiki_page(
            auth, request.owner, request.repo, request.title, 
            request.content, request.installation_id
        )
    
    @app.post("/tools/update_wiki_page", operation_id="update_wiki_page", summary="Update a wiki page")
    async def update_wiki_endpoint(request: WikiPageRequest) -> Dict[str, Any]:
        """Updates an existing wiki page in a GitHub repository."""
        return await update_wiki_page(
            auth, request.owner, request.repo, request.title, 
            request.content, request.installation_id
        )
    
    @app.post("/tools/delete_wiki_page", operation_id="delete_wiki_page", summary="Delete a wiki page")
    async def delete_wiki_endpoint(request: DeleteWikiPageRequest) -> Dict[str, Any]:
        """Deletes a wiki page from a GitHub repository."""
        return await delete_wiki_page(
            auth, request.owner, request.repo, request.title, request.installation_id
        )
    
    @app.post("/tools/trigger_workflow", operation_id="trigger_workflow", summary="Trigger a GitHub Actions workflow")
    async def trigger_workflow_endpoint(request: TriggerWorkflowRequest) -> Dict[str, Any]:
        """Triggers a GitHub Actions workflow."""
        return await trigger_workflow(
            auth, request.owner, request.repo, request.workflow_id,
            request.ref, request.inputs, request.installation_id
        )
    
    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {"status": "healthy", "service": "github-mcp-server"}
    
    @app.get("/")
    async def root():
        """Root endpoint with service information."""
        return {
            "service": "GitHub MCP Server",
            "version": "0.1.0",
            "description": "Model Context Protocol server for GitHub integration with HTTP transport",
            "transport": "HTTP (FastAPI-MCP)",
            "endpoints": {
                "health": "/health",
                "webhooks": "/webhooks/github",
                "actions": "/actions/{owner}/{repo}/dispatch",
                "mcp": "/mcp/",
                "tools": "/tools/"
            },
            "usage": {
                "description": "Use /tools/ endpoints directly or /mcp/ for MCP protocol communication",
                "note": "MCP endpoints are automatically provided by FastAPI-MCP"
            }
        }
    
    # Initialize FastAPI-MCP integration
    mcp = FastApiMCP(
        app,
        name="GitHub MCP Server", 
        description="A GitHub integration API exposed as an MCP server"
    )
    mcp.mount()
    
    return app


# Create the application instance
app = create_app()


if __name__ == "__main__":
    import uvicorn
    
    config = get_config()
    
    uvicorn.run(
        "github_mcp_server.main:app",
        host=config.server_host,
        port=config.server_port,
        reload=config.debug,
    )
