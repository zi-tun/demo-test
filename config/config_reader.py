"""
Configuration reader for INI files and credential management.
Supports reading from config.ini for OAuth-based API access.
"""

import configparser
import os
from typing import Dict, Optional, Any
import requests
from dataclasses import dataclass


@dataclass
class OAuthCredentials:
    """OAuth credentials for API access."""
    client_id: str
    client_secret: str
    app_key: str
    grant_type: str
    token_url: str
    access_token: Optional[str] = None


class ConfigReader:
    """Configuration reader for INI files and OAuth management."""
    
    def __init__(self, config_file: str = "config/config.ini"):
        """Initialize config reader with INI file path."""
        self.config_file = config_file
        self.config = configparser.ConfigParser()
        self._load_config()
    
    def _load_config(self) -> None:
        """Load configuration from INI file."""
        if os.path.exists(self.config_file):
            self.config.read(self.config_file)
        else:
            raise FileNotFoundError(f"Configuration file not found: {self.config_file}")
    
    def get_oauth_credentials(self, section: str = "OPENAI") -> OAuthCredentials:
        """Get OAuth credentials from config section."""
        if section not in self.config:
            raise ValueError(f"Section '{section}' not found in config file")
        
        section_config = self.config[section]
        
        return OAuthCredentials(
            client_id=section_config.get('client_id'),
            client_secret=section_config.get('client_secret'),
            app_key=section_config.get('appKey'),
            grant_type=section_config.get('grant_type', 'client_credentials'),
            token_url=section_config.get('token_url')
        )
    
    def get_access_token(self, credentials: OAuthCredentials) -> str:
        """Get access token using OAuth credentials."""
        try:
            payload = {
                'grant_type': credentials.grant_type,
                'client_id': credentials.client_id,
                'client_secret': credentials.client_secret
            }
            
            response = requests.post(credentials.token_url, data=payload)
            response.raise_for_status()
            
            token_data = response.json()
            return token_data.get('access_token')
            
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to obtain access token: {str(e)}")
    
    def get_config_value(self, section: str, key: str, default: Any = None) -> Any:
        """Get a specific configuration value."""
        try:
            return self.config.get(section, key)
        except (configparser.NoSectionError, configparser.NoOptionError):
            return default


# Global config reader instance
config_reader = None


def get_config_reader() -> ConfigReader:
    """Get the global config reader instance."""
    global config_reader
    if config_reader is None:
        try:
            config_reader = ConfigReader()
        except FileNotFoundError:
            # Fallback - config.ini not required if using .env
            config_reader = None
    return config_reader
