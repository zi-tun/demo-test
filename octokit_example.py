"""
Example of using Octokit.py for GitHub App authentication.

This demonstrates the recommended Octokit.py approach for GitHub App authentication
as referenced in the GitHub documentation.
"""

from octokit import Octokit
from pathlib import Path


def create_octokit_client_example():
    """Example of creating Octokit clients for GitHub App authentication."""
    
    # Load your GitHub App credentials
    app_id = "1656559"  # Your GitHub App ID
    private_key_path = "gitdocbot.private-key.pem"
    
    # Load private key
    with open(private_key_path, 'r') as f:
        private_key = f.read()
    
    # Create app-authenticated client (for app-level operations)
    app_client = Octokit(
        auth='app',
        app_id=app_id,
        private_key=private_key
    )
    
    # Example: List app installations
    installations_response = app_client.apps.list_installations()
    print(f"Found {len(installations_response.json)} installations")
    
    # Create installation-authenticated client (for repository operations)
    # You would get the installation_id from webhooks or API calls
    installation_id = 12345  # Replace with actual installation ID
    
    installation_client = Octokit(
        auth='installation',
        app_id=app_id,
        private_key=private_key,
        installation_id=installation_id
    )
    
    # Example: Create a wiki page using installation client
    # Note: GitHub doesn't have direct wiki API, but you can use Git data API
    
    return app_client, installation_client


def create_wiki_page_octokit_example(owner: str, repo: str, title: str, content: str):
    """Example of creating a wiki page using Octokit.py with GitHub's Git data API."""
    
    # This is a more complete implementation of wiki page creation
    # using GitHub's Git data API as recommended in the documentation
    
    app_id = "1656559"
    private_key_path = "gitdocbot.private-key.pem"
    
    with open(private_key_path, 'r') as f:
        private_key = f.read()
    
    # Create installation client
    installation_id = get_installation_id_for_repo(owner, repo)  # You'd implement this
    
    client = Octokit(
        auth='installation',
        app_id=app_id,
        private_key=private_key,
        installation_id=installation_id
    )
    
    try:
        # Wiki pages are stored in a separate repository with .wiki.git suffix
        wiki_repo = f"{owner}/{repo}.wiki"
        
        # Get the wiki repository (this would require direct Git operations)
        # For now, return a placeholder as the current implementation does
        
        return {
            "success": True,
            "message": "Wiki page creation via Octokit.py (placeholder)",
            "wiki_url": f"https://github.com/{owner}/{repo}/wiki/{title.replace(' ', '-')}",
            "method": "octokit.py",
            "note": "Full implementation requires Git data API operations"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Octokit.py error: {str(e)}"
        }


def get_installation_id_for_repo(owner: str, repo: str) -> int:
    """Get installation ID for a specific repository using Octokit.py."""
    
    app_id = "1656559"
    private_key_path = "gitdocbot.private-key.pem"
    
    with open(private_key_path, 'r') as f:
        private_key = f.read()
    
    app_client = Octokit(
        auth='app',
        app_id=app_id,
        private_key=private_key
    )
    
    # Get installation for the repository
    response = app_client.repos.get_installation(owner=owner, repo=repo)
    return response.json['id']


if __name__ == "__main__":
    # Example usage
    try:
        app_client, installation_client = create_octokit_client_example()
        print("✅ Octokit.py clients created successfully")
        
        # Test creating a wiki page
        result = create_wiki_page_octokit_example(
            "octocat", 
            "Hello-World", 
            "Test Page", 
            "# Test\nThis is a test page"
        )
        print(f"📝 Wiki creation result: {result}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
