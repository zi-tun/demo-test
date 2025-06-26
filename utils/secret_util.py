"""
Secret utility for handling configuration files.
Supports loading properties from configuration files.
"""

import os
import configparser
from typing import Dict, Any


def collect_property_file_contents(section: str, config_file: str = "config/openai.properties") -> Dict[str, str]:
    """
    Load configuration properties from a file.
    
    Args:
        section: Configuration section name
        config_file: Path to the configuration file
        
    Returns:
        Dictionary containing configuration properties
    """
    config = configparser.ConfigParser()
    
    # Try multiple possible locations
    possible_paths = [
        config_file,
        f"config/{section}.properties",
        f"config/{section}.ini",
        f"{section}.properties",
        f"{section}.ini"
    ]
    
    config_path = None
    for path in possible_paths:
        if os.path.exists(path):
            config_path = path
            break
    
    if not config_path:
        raise FileNotFoundError(f"Configuration file not found. Tried: {possible_paths}")
    
    config.read(config_path)
    
    if section not in config:
        raise ValueError(f"Section '{section}' not found in configuration file {config_path}")
    
    return dict(config[section])


def collect_property_file_contents_env(section: str) -> Dict[str, str]:
    """
    Load configuration from environment variables.
    
    Args:
        section: Configuration section name (used as prefix)
        
    Returns:
        Dictionary containing configuration properties
    """
    prefix = f"{section.upper()}_"
    config = {}
    
    for key, value in os.environ.items():
        if key.startswith(prefix):
            config_key = key[len(prefix):].lower()
            config[config_key] = value
    
    return config
