#!/usr/bin/env python3
"""
Quick setup script for configuring API tokens.
Interactive script to help set up your .env file.
"""

import os
import sys
from pathlib import Path

def setup_environment():
    """Interactive setup for environment configuration."""
    print("🚀 LangGraph Multi-Agent System - Quick Setup")
    print("=" * 50)
    
    env_file = Path(".env")
    
    # Check if .env exists
    if not env_file.exists():
        print("📋 Creating .env file from template...")
        if Path(".env.example").exists():
            with open(".env.example", "r") as src, open(".env", "w") as dst:
                dst.write(src.read())
            print("✅ Created .env file")
        else:
            print("❌ .env.example not found!")
            return False
    
    # Read current .env
    with open(".env", "r") as f:
        lines = f.readlines()
    
    # Interactive configuration
    print("\n🔑 Let's set up your API keys:")
    print("(Press Enter to skip optional keys)")
    
    # OpenAI API Key
    print("\n1. OpenAI API Key (Required)")
    print("   Get yours at: https://platform.openai.com/api-keys")
    current_openai = ""
    for line in lines:
        if line.startswith("OPENAI_API_KEY="):
            current_openai = line.split("=", 1)[1].strip()
            break
    
    if current_openai and current_openai not in ["your_openai_api_key_here", "demo-key-for-testing-only"]:
        print(f"   Current: {current_openai[:10]}...{current_openai[-4:]}")
        use_current = input("   Keep current key? (y/n): ").lower().startswith('y')
        if use_current:
            openai_key = current_openai
        else:
            openai_key = input("   Enter your OpenAI API key: ").strip()
    else:
        openai_key = input("   Enter your OpenAI API key: ").strip()
    
    # Anthropic API Key (optional)
    print("\n2. Anthropic API Key (Optional)")
    print("   Get yours at: https://console.anthropic.com/settings/keys")
    anthropic_key = input("   Enter your Anthropic API key (or press Enter to skip): ").strip()
    
    # Demo Mode
    print("\n3. Demo Mode")
    print("   Set to 'false' to use real APIs, 'true' for mock responses")
    if openai_key or anthropic_key:
        demo_mode = input("   Enable demo mode? (y/n) [default: n]: ").lower()
        demo_mode = "true" if demo_mode.startswith('y') else "false"
    else:
        print("   No API keys provided, keeping demo mode enabled")
        demo_mode = "true"
    
    # Update .env file
    print("\n💾 Updating .env file...")
    
    new_lines = []
    updated_keys = set()
    
    for line in lines:
        if line.startswith("OPENAI_API_KEY="):
            if openai_key:
                new_lines.append(f"OPENAI_API_KEY={openai_key}\n")
                updated_keys.add("OPENAI_API_KEY")
            else:
                new_lines.append("# OPENAI_API_KEY=your_openai_api_key_here\n")
        elif line.startswith("ANTHROPIC_API_KEY=") or line.startswith("# ANTHROPIC_API_KEY="):
            if anthropic_key:
                new_lines.append(f"ANTHROPIC_API_KEY={anthropic_key}\n")
                updated_keys.add("ANTHROPIC_API_KEY")
            else:
                new_lines.append("# ANTHROPIC_API_KEY=your_anthropic_api_key_here\n")
        elif line.startswith("DEMO_MODE=") or line.startswith("# DEMO_MODE="):
            new_lines.append(f"DEMO_MODE={demo_mode}\n")
            updated_keys.add("DEMO_MODE")
        else:
            new_lines.append(line)
    
    # Add missing keys
    if "DEMO_MODE" not in updated_keys:
        new_lines.append(f"\n# Demo mode (set to true to run without real API calls)\nDEMO_MODE={demo_mode}\n")
    
    # Write updated .env
    with open(".env", "w") as f:
        f.writelines(new_lines)
    
    print("✅ Environment file updated!")
    
    # Summary
    print("\n📊 Configuration Summary:")
    print(f"   OpenAI API: {'✅ Configured' if openai_key else '❌ Not set'}")
    print(f"   Anthropic API: {'✅ Configured' if anthropic_key else '⚠️  Not set (optional)'}")
    print(f"   Demo Mode: {'⚠️  Enabled' if demo_mode == 'true' else '✅ Disabled'}")
    
    # Next steps
    print("\n🎯 Next Steps:")
    if openai_key or anthropic_key:
        print("1. Run the token checker: python check_tokens.py")
        print("2. Test the system: python main.py --query 'Hello world'")
        if demo_mode == "true":
            print("3. To use real APIs, set DEMO_MODE=false in .env")
    else:
        print("1. Get an API key from OpenAI or Anthropic")
        print("2. Run this script again to configure it")
        print("3. The system will run in demo mode until you add real API keys")
    
    return True

def main():
    """Main setup function."""
    try:
        setup_environment()
    except KeyboardInterrupt:
        print("\n\n👋 Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Setup failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
