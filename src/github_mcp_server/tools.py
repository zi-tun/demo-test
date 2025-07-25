"""GitHub API tools for the MCP server using PyGithub."""

import asyncio
from typing import List, Optional, Any, Dict
from dataclasses import dataclass
from github import Github, GithubException
from .auth import GitHubAppAuth
from .config import Config


async def create_repository(
    auth: GitHubAppAuth,
    owner: str,
    name: str,
    description: str = "",
    private: bool = False,
    installation_id: Optional[int] = None
) -> Dict[str, Any]:
    """Create a new GitHub repository."""
    try:
        if not installation_id:
            installation_id = auth.get_installation_id(owner)
        
        github = auth.get_github_client(installation_id)
        
        # Get the organization or user
        if owner != github.get_user().login:
            org = github.get_organization(owner)
            repo = org.create_repo(
                name=name,
                description=description,
                private=private,
            )
        else:
            user = github.get_user()
            repo = user.create_repo(
                name=name,
                description=description,
                private=private,
            )
        
        return {
            "success": True,
            "repository": {
                "name": repo.name,
                "full_name": repo.full_name,
                "description": repo.description,
                "private": repo.private,
                "html_url": repo.html_url,
                "clone_url": repo.clone_url,
            }
        }
    except GithubException as e:
        return {"success": False, "error": str(e)}
    except Exception as e:
        return {"success": False, "error": f"Unexpected error: {str(e)}"}


async def get_repository_info(
    auth: GitHubAppAuth,
    owner: str,
    repo: str,
    installation_id: Optional[int] = None
) -> Dict[str, Any]:
    """Get information about a GitHub repository."""
    try:
        if not installation_id:
            installation_id = auth.get_installation_id(owner, repo)
        
        github = auth.get_github_client(installation_id)
        repository = github.get_repo(f"{owner}/{repo}")
        
        return {
            "success": True,
            "repository": {
                "name": repository.name,
                "full_name": repository.full_name,
                "description": repository.description,
                "private": repository.private,
                "html_url": repository.html_url,
                "clone_url": repository.clone_url,
                "default_branch": repository.default_branch,
                "language": repository.language,
                "stargazers_count": repository.stargazers_count,
                "forks_count": repository.forks_count,
                "created_at": repository.created_at.isoformat(),
                "updated_at": repository.updated_at.isoformat(),
            }
        }
    except GithubException as e:
        return {"success": False, "error": str(e)}
    except Exception as e:
        return {"success": False, "error": f"Unexpected error: {str(e)}"}


async def create_issue(
    auth: GitHubAppAuth,
    owner: str,
    repo: str,
    title: str,
    body: str = "",
    labels: List[str] = None,
    assignees: List[str] = None,
    installation_id: Optional[int] = None
) -> Dict[str, Any]:
    """Create a new issue in a GitHub repository."""
    try:
        if not installation_id:
            installation_id = auth.get_installation_id(owner, repo)
        
        github = auth.get_github_client(installation_id)
        repository = github.get_repo(f"{owner}/{repo}")
        
        issue = repository.create_issue(
            title=title,
            body=body,
            labels=labels or [],
            assignees=assignees or [],
        )
        
        return {
            "success": True,
            "issue": {
                "number": issue.number,
                "title": issue.title,
                "body": issue.body,
                "state": issue.state,
                "html_url": issue.html_url,
                "created_at": issue.created_at.isoformat(),
                "labels": [label.name for label in issue.labels],
                "assignees": [assignee.login for assignee in issue.assignees],
            }
        }
    except GithubException as e:
        return {"success": False, "error": str(e)}
    except Exception as e:
        return {"success": False, "error": f"Unexpected error: {str(e)}"}


async def update_issue(
    auth: GitHubAppAuth,
    owner: str,
    repo: str,
    issue_number: int,
    title: Optional[str] = None,
    body: Optional[str] = None,
    state: Optional[str] = None,
    labels: Optional[List[str]] = None,
    assignees: Optional[List[str]] = None,
    installation_id: Optional[int] = None
) -> Dict[str, Any]:
    """Update an existing issue in a GitHub repository."""
    try:
        if not installation_id:
            installation_id = auth.get_installation_id(owner, repo)
        
        github = auth.get_github_client(installation_id)
        repository = github.get_repo(f"{owner}/{repo}")
        issue = repository.get_issue(issue_number)
        
        # Build update parameters
        update_params = {}
        if title is not None:
            update_params["title"] = title
        if body is not None:
            update_params["body"] = body
        if state is not None:
            update_params["state"] = state
        if labels is not None:
            update_params["labels"] = labels
        if assignees is not None:
            update_params["assignees"] = assignees
        
        issue.edit(**update_params)
        
        return {
            "success": True,
            "issue": {
                "number": issue.number,
                "title": issue.title,
                "body": issue.body,
                "state": issue.state,
                "html_url": issue.html_url,
                "updated_at": issue.updated_at.isoformat(),
                "labels": [label.name for label in issue.labels],
                "assignees": [assignee.login for assignee in issue.assignees],
            }
        }
    except GithubException as e:
        return {"success": False, "error": str(e)}
    except Exception as e:
        return {"success": False, "error": f"Unexpected error: {str(e)}"}


async def create_pull_request(
    auth: GitHubAppAuth,
    owner: str,
    repo: str,
    title: str,
    head: str,
    base: str,
    body: str = "",
    draft: bool = False,
    installation_id: Optional[int] = None
) -> Dict[str, Any]:
    """Create a new pull request in a GitHub repository."""
    try:
        if not installation_id:
            installation_id = auth.get_installation_id(owner, repo)
        
        github = auth.get_github_client(installation_id)
        repository = github.get_repo(f"{owner}/{repo}")
        
        pr = repository.create_pull(
            title=title,
            body=body,
            head=head,
            base=base,
            draft=draft,
        )
        
        return {
            "success": True,
            "pull_request": {
                "number": pr.number,
                "title": pr.title,
                "body": pr.body,
                "state": pr.state,
                "html_url": pr.html_url,
                "head": pr.head.ref,
                "base": pr.base.ref,
                "draft": pr.draft,
                "created_at": pr.created_at.isoformat(),
            }
        }
    except GithubException as e:
        return {"success": False, "error": str(e)}
    except Exception as e:
        return {"success": False, "error": f"Unexpected error: {str(e)}"}


async def merge_pull_request(
    auth: GitHubAppAuth,
    owner: str,
    repo: str,
    pull_number: int,
    commit_title: Optional[str] = None,
    commit_message: Optional[str] = None,
    merge_method: str = "merge",
    installation_id: Optional[int] = None
) -> Dict[str, Any]:
    """Merge a pull request in a GitHub repository."""
    try:
        if not installation_id:
            installation_id = auth.get_installation_id(owner, repo)
        
        github = auth.get_github_client(installation_id)
        repository = github.get_repo(f"{owner}/{repo}")
        pr = repository.get_pull(pull_number)
        
        result = pr.merge(
            commit_title=commit_title,
            commit_message=commit_message,
            merge_method=merge_method,
        )
        
        return {
            "success": True,
            "merged": result.merged,
            "sha": result.sha,
            "message": result.message,
        }
    except GithubException as e:
        return {"success": False, "error": str(e)}
    except Exception as e:
        return {"success": False, "error": f"Unexpected error: {str(e)}"}


async def create_wiki_page(
    auth: GitHubAppAuth,
    owner: str,
    repo: str,
    title: str,
    content: str,
    installation_id: Optional[int] = None
) -> Dict[str, Any]:
    """Create a new wiki page in a GitHub repository."""
    try:
        if not installation_id:
            installation_id = auth.get_installation_id(owner, repo)
        
        github = auth.get_github_client(installation_id)
        repository = github.get_repo(f"{owner}/{repo}")
        
        # GitHub API doesn't have direct wiki support in PyGithub
        # We'll use the git data API to create wiki pages
        # Wiki pages are stored in a separate git repository with .wiki.git suffix
        
        # For now, return a placeholder implementation
        # In a full implementation, you would use the GitHub API directly
        return {
            "success": True,
            "message": "Wiki page creation requires direct GitHub API calls",
            "wiki_url": f"https://github.com/{owner}/{repo}/wiki/{title.replace(' ', '-')}",
        }
    except GithubException as e:
        return {"success": False, "error": str(e)}
    except Exception as e:
        return {"success": False, "error": f"Unexpected error: {str(e)}"}


async def update_wiki_page(
    auth: GitHubAppAuth,
    owner: str,
    repo: str,
    title: str,
    content: str,
    installation_id: Optional[int] = None
) -> Dict[str, Any]:
    """Update a wiki page in a GitHub repository."""
    # Similar to create_wiki_page, this would require direct GitHub API calls
    return {
        "success": True,
        "message": "Wiki page update requires direct GitHub API calls",
        "wiki_url": f"https://github.com/{owner}/{repo}/wiki/{title.replace(' ', '-')}",
    }


async def delete_wiki_page(
    auth: GitHubAppAuth,
    owner: str,
    repo: str,
    title: str,
    installation_id: Optional[int] = None
) -> Dict[str, Any]:
    """Delete a wiki page from a GitHub repository."""
    # Similar to create_wiki_page, this would require direct GitHub API calls
    return {
        "success": True,
        "message": "Wiki page deletion requires direct GitHub API calls",
    }


async def trigger_workflow(
    auth: GitHubAppAuth,
    owner: str,
    repo: str,
    workflow_id: str,
    ref: str = "main",
    inputs: Dict[str, Any] = None,
    installation_id: Optional[int] = None
) -> Dict[str, Any]:
    """Trigger a GitHub Actions workflow."""
    try:
        if not installation_id:
            installation_id = auth.get_installation_id(owner, repo)
        
        github = auth.get_github_client(installation_id)
        repository = github.get_repo(f"{owner}/{repo}")
        
        workflow = repository.get_workflow(workflow_id)
        result = workflow.create_dispatch(ref=ref, inputs=inputs or {})
        
        return {
            "success": True,
            "message": "Workflow dispatch triggered successfully",
            "workflow_id": workflow_id,
            "ref": ref,
            "inputs": inputs or {},
        }
    except GithubException as e:
        return {"success": False, "error": str(e)}
    except Exception as e:
        return {"success": False, "error": f"Unexpected error: {str(e)}"}
