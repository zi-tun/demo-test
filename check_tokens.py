#!/usr/bin/env python3
"""
API Token Checker for LangGraph Multi-Agent System
Validates that your API keys are properly configured and working.
"""

import os
import sys
from dotenv import load_dotenv
from typing import Dict, List, Tuple

# Load environment variables
load_dotenv()

def check_openai_api() -> Tuple[bool, str]:
    """Check OpenAI API key and connection."""
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        return False, "❌ OPENAI_API_KEY not found in environment"
    
    if api_key == "demo-key-for-testing-only" or api_key == "your_openai_api_key_here":
        return False, "❌ OPENAI_API_KEY is still set to placeholder value"
    
    if not api_key.startswith("sk-"):
        return False, "❌ OPENAI_API_KEY format appears invalid (should start with 'sk-')"
    
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        
        # Test with a minimal request
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=1
        )
        return True, "✅ OpenAI API key is valid and working"
        
    except ImportError:
        return False, "❌ OpenAI package not installed (run: pip install openai)"
    except Exception as e:
        return False, f"❌ OpenAI API error: {str(e)}"

def check_anthropic_api() -> Tuple[bool, str]:
    """Check Anthropic API key and connection."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    
    if not api_key:
        return False, "⚠️  ANTHROPIC_API_KEY not found (optional)"
    
    if api_key == "your_anthropic_api_key_here":
        return False, "❌ ANTHROPIC_API_KEY is still set to placeholder value"
    
    try:
        from anthropic import Anthropic
        client = Anthropic(api_key=api_key)
        
        # Test with a minimal request
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=1,
            messages=[{"role": "user", "content": "Hi"}]
        )
        return True, "✅ Anthropic API key is valid and working"
        
    except ImportError:
        return False, "❌ Anthropic package not installed (run: pip install anthropic)"
    except Exception as e:
        return False, f"❌ Anthropic API error: {str(e)}"

def check_cisco_openai() -> Tuple[bool, str]:
    """Check Cisco OpenAI configuration and connection."""
    try:
        from utils.llm_client import CiscoOpenAIClient
        
        # Try to create a client
        client = CiscoOpenAIClient()
        
        if client.is_available():
            return True, "✅ Cisco OpenAI configuration is valid and working"
        else:
            return False, "❌ Cisco OpenAI configuration invalid or token request failed"
            
    except FileNotFoundError as e:
        return False, f"⚠️  Cisco OpenAI config file not found: {str(e)}"
    except ValueError as e:
        return False, f"❌ Cisco OpenAI configuration error: {str(e)}"
    except ImportError:
        return False, "❌ Required packages not installed for Cisco OpenAI"
    except Exception as e:
        return False, f"❌ Cisco OpenAI error: {str(e)}"

def check_demo_mode() -> Tuple[bool, str]:
    """Check if demo mode is enabled."""
    demo_mode = os.getenv("DEMO_MODE", "").lower() in ["true", "1", "yes"]
    
    if demo_mode:
        return False, "⚠️  Demo mode is enabled - set DEMO_MODE=false to use real APIs"
    else:
        return True, "✅ Demo mode is disabled - will use real APIs"

def check_environment_file() -> Tuple[bool, str]:
    """Check if .env file exists and is readable."""
    if not os.path.exists(".env"):
        return False, "❌ .env file not found - copy .env.example to .env"
    
    try:
        with open(".env", "r") as f:
            content = f.read()
        
        if "your_openai_api_key_here" in content:
            return False, "⚠️  .env file contains placeholder values"
        
        return True, "✅ .env file exists and appears configured"
        
    except Exception as e:
        return False, f"❌ Error reading .env file: {str(e)}"

def main():
    """Main token checking function."""
    print("🔐 API Token Checker for LangGraph Multi-Agent System")
    print("=" * 60)
    
    checks = [
        ("Environment File", check_environment_file),
        ("Demo Mode", check_demo_mode),
        ("OpenAI API", check_openai_api),
        ("Anthropic API", check_anthropic_api),
        ("Cisco OpenAI", check_cisco_openai),
    ]
    
    results = []
    for name, check_func in checks:
        try:
            success, message = check_func()
            results.append((name, success, message))
            print(f"{name:20} | {message}")
        except Exception as e:
            results.append((name, False, f"Error: {str(e)}"))
            print(f"{name:20} | ❌ Error: {str(e)}")
    
    print("\n" + "=" * 60)
    
    # Summary
    successes = sum(1 for _, success, _ in results if success)
    total = len(results)
    
    print(f"Summary: {successes}/{total} checks passed")
    
    # Check if system is ready
    openai_working = any(name == "OpenAI API" and success for name, success, _ in results)
    anthropic_working = any(name == "Anthropic API" and success for name, success, _ in results)
    cisco_openai_working = any(name == "Cisco OpenAI" and success for name, success, _ in results)
    demo_disabled = any(name == "Demo Mode" and success for name, success, _ in results)
    
    if (openai_working or anthropic_working or cisco_openai_working) and demo_disabled:
        print("\n🎉 System is ready to run with real APIs!")
        print("\nTo test your setup, run:")
        print("  python main.py --query 'Hello, test my configuration'")
    else:
        print("\n⚠️  System is not ready for production use.")
        print("\nNext steps:")
        
        if not (openai_working or anthropic_working or cisco_openai_working):
            print("  1. Get an API key from OpenAI (recommended) or Anthropic")
            print("     - OpenAI: https://platform.openai.com/api-keys")
            print("     - Anthropic: https://console.anthropic.com/settings/keys")
            print("  2. Add your API key to the .env file")
        
        if not demo_disabled:
            print("  3. Set DEMO_MODE=false in your .env file")
        
        print("\nSee API_TOKENS_GUIDE.md for detailed instructions.")

if __name__ == "__main__":
    main()
