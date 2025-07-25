"""GitHub Actions API endpoints."""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from github_mcp_server.auth import GitHubAppAuth
from github_mcp_server.config import get_config

router = APIRouter(tags=["GitHub Actions"])


class WorkflowDispatchRequest(BaseModel):
    """Request model for workflow dispatch."""
    ref: str = "main"
    inputs: Optional[Dict[str, Any]] = None


def get_github_auth() -> GitHubAppAuth:
    """Dependency to get GitHub authentication."""
    return GitHubAppAuth()


@router.post("/{owner}/{repo}/dispatch")
async def dispatch_workflow(
    owner: str,
    repo: str,
    workflow_id: str,
    request: WorkflowDispatchRequest,
    installation_id: Optional[int] = None,
    auth: GitHubAppAuth = Depends(get_github_auth)
):
    """Dispatch a GitHub Actions workflow."""
    try:
        github = auth.get_github_client(installation_id)
        repo_obj = github.get_repo(f"{owner}/{repo}")
        
        # Trigger workflow dispatch
        success = repo_obj.create_workflow_dispatch(
            workflow_id,
            ref=request.ref,
            inputs=request.inputs or {}
        )
        
        return {
            "message": "Workflow dispatch triggered successfully",
            "workflow_id": workflow_id,
            "ref": request.ref,
            "success": success
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{owner}/{repo}/workflows")
async def list_workflows(
    owner: str,
    repo: str,
    installation_id: Optional[int] = None,
    auth: GitHubAppAuth = Depends(get_github_auth)
):
    """List workflows for a repository."""
    try:
        github = auth.get_github_client(installation_id)
        repo_obj = github.get_repo(f"{owner}/{repo}")
        
        workflows = repo_obj.get_workflows()
        
        workflow_list = []
        for workflow in workflows:
            workflow_list.append({
                "id": workflow.id,
                "name": workflow.name,
                "path": workflow.path,
                "state": workflow.state,
                "created_at": workflow.created_at.isoformat(),
                "updated_at": workflow.updated_at.isoformat(),
                "url": workflow.url,
                "html_url": workflow.html_url,
                "badge_url": workflow.badge_url
            })
        
        return {
            "workflows": workflow_list,
            "total_count": len(workflow_list)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{owner}/{repo}/workflows/{workflow_id}/runs")
async def list_workflow_runs(
    owner: str,
    repo: str,
    workflow_id: str,
    limit: int = 10,
    installation_id: Optional[int] = None,
    auth: GitHubAppAuth = Depends(get_github_auth)
):
    """List workflow runs for a specific workflow."""
    try:
        github = auth.get_github_client(installation_id)
        repo_obj = github.get_repo(f"{owner}/{repo}")
        
        workflow = repo_obj.get_workflow(workflow_id)
        runs = workflow.get_runs()
        
        run_list = []
        count = 0
        for run in runs:
            if count >= limit:
                break
            
            run_list.append({
                "id": run.id,
                "name": run.name,
                "head_branch": run.head_branch,
                "head_sha": run.head_sha,
                "status": run.status,
                "conclusion": run.conclusion,
                "workflow_id": run.workflow_id,
                "check_suite_id": run.check_suite_id,
                "created_at": run.created_at.isoformat(),
                "updated_at": run.updated_at.isoformat(),
                "url": run.url,
                "html_url": run.html_url,
                "jobs_url": run.jobs_url,
                "logs_url": run.logs_url,
                "check_suite_url": run.check_suite_url,
                "cancel_url": run.cancel_url,
                "rerun_url": run.rerun_url,
                "workflow_url": run.workflow_url
            })
            count += 1
        
        return {
            "workflow_runs": run_list,
            "total_count": len(run_list)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
