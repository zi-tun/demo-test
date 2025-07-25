"""Configuration management for GitHub MCP Server."""

import configparser
import os
from pathlib import Path
from typing import Optional


class Config:
    """Configuration manager for GitHub MCP Server."""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize configuration.
        
        Args:
            config_path: Path to config file. If None, looks for config/config.ini
        """
        self.config = configparser.ConfigParser()
        
        if config_path is None:
            # Default config path relative to project root
            project_root = Path(__file__).parent.parent.parent
            config_path = project_root / "config" / "config.ini"
        
        self.config_path = Path(config_path)
        self._load_config()
    
    def _load_config(self) -> None:
        """Load configuration from file."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        
        self.config.read(self.config_path)
    
    # GitHub configuration
    @property
    def github_app_id(self) -> int:
        """Get GitHub App ID."""
        return self.config.getint('github', 'app_id')
    
    @property
    def github_private_key_path(self) -> str:
        """Get GitHub private key path."""
        return self.config.get('github', 'private_key_path')
    
    @property
    def github_webhook_secret(self) -> str:
        """Get GitHub webhook secret."""
        return self.config.get('github', 'webhook_secret')
    
    # Server configuration
    @property
    def server_host(self) -> str:
        """Get server host."""
        return self.config.get('server', 'host')
    
    @property
    def server_port(self) -> int:
        """Get server port."""
        return self.config.getint('server', 'port')
    
    # General configuration
    @property
    def debug(self) -> bool:
        """Get debug mode."""
        return self.config.getboolean('general', 'debug')


# Global config instance
_config = None


def get_config(config_path: Optional[str] = None) -> Config:
    """Get global configuration instance.
    
    Args:
        config_path: Path to config file. Only used on first call.
        
    Returns:
        Configuration instance
    """
    global _config
    if _config is None:
        _config = Config(config_path)
    return _config
