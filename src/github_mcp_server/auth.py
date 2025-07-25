"""GitHub App authentication for MCP server."""

import jwt
import time
from pathlib import Path
from typing import Optional
from github import Github, Auth
from cryptography.hazmat.primitives import serialization
from github_mcp_server.config import get_config


class GitHubAppAuth:
    """GitHub App authentication handler."""
    
    def __init__(self, app_id: Optional[int] = None, private_key_path: Optional[str] = None):
        """Initialize GitHub App authentication.
        
        Args:
            app_id: GitHub App ID. If None, loads from config.
            private_key_path: Path to private key file. If None, loads from config.
        """
        config = get_config()
        
        self.app_id = app_id or config.github_app_id
        self.private_key_path = private_key_path or config.github_private_key_path
        self._private_key = self._load_private_key()
    
    def _load_private_key(self) -> str:
        """Load private key from file."""
        key_path = Path(self.private_key_path)
        if not key_path.exists():
            raise FileNotFoundError(f"Private key file not found: {self.private_key_path}")
        
        with open(key_path, 'r') as f:
            return f.read()
    
    def create_jwt_token(self) -> str:
        """Create JWT token for GitHub App authentication."""
        now = int(time.time())
        payload = {
            'iat': now - 60,  # Issued at time (60 seconds ago to account for clock skew)
            'exp': now + 600,  # Expiration time (10 minutes from now)
            'iss': self.app_id,  # Issuer (GitHub App ID)
        }
        
        # Load private key for signing
        private_key_obj = serialization.load_pem_private_key(
            self._private_key.encode(),
            password=None
        )
        
        # Create and return JWT
        return jwt.encode(payload, private_key_obj, algorithm='RS256')
    
    def get_github_client(self, installation_id: Optional[int] = None) -> Github:
        """Get authenticated GitHub client.
        
        Args:
            installation_id: GitHub App installation ID. If provided, returns
                           installation-authenticated client. Otherwise returns
                           app-authenticated client.
        
        Returns:
            Authenticated GitHub client
        """
        if installation_id:
            # Get installation access token
            auth = Auth.AppInstallationAuth(
                app_id=self.app_id,
                private_key=self._private_key,
                installation_id=installation_id
            )
        else:
            # Use app authentication
            auth = Auth.AppAuth(
                app_id=self.app_id,
                private_key=self._private_key
            )
        
        return Github(auth=auth)
    
    async def get_installation_id(self, owner: str, repo: Optional[str] = None) -> int:
        """Get installation ID for a repository or organization.
        
        Args:
            owner: Repository owner or organization name
            repo: Repository name (optional)
        
        Returns:
            Installation ID
        
        Raises:
            ValueError: If installation not found
        """
        octokit = self.get_github_client()
        
        try:
            if repo:
                # Get installation for specific repository
                response = octokit.repos.get_installation(owner=owner, repo=repo)
                return response.json['id']
            else:
                # Get installations for the app
                response = octokit.apps.list_installations()
                installations = response.json
                
                for installation in installations:
                    if installation['account']['login'] == owner:
                        return installation['id']
                
                raise ValueError(f"No installation found for {owner}")
            
        except Exception as e:
            raise ValueError(f"Failed to get installation ID for {owner}/{repo or ''}: {e}")
    
    def verify_webhook_signature(self, payload: bytes, signature: str, secret: str) -> bool:
        """Verify GitHub webhook signature.
        
        Args:
            payload: Raw webhook payload
            signature: GitHub signature from X-Hub-Signature-256 header
            secret: Webhook secret
        
        Returns:
            True if signature is valid, False otherwise
        """
        import hmac
        import hashlib
        
        expected_signature = 'sha256=' + hmac.new(
            secret.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(expected_signature, signature)
