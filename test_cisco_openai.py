#!/usr/bin/env python3
"""
Test script for Cisco Enterprise OpenAI configuration.
Use this to verify your Cisco OpenAI setup is working correctly.
"""

import sys
from typing import Dict, Any

def test_cisco_openai_config():
    """Test Cisco OpenAI configuration and token generation."""
    print("🧪 Testing Cisco Enterprise OpenAI Configuration")
    print("=" * 50)
    
    try:
        from utils.llm_client import CiscoOpenAIClient
        from utils.secret_util import collect_property_file_contents
        
        # Test configuration loading
        print("1. Testing configuration loading...")
        try:
            config = collect_property_file_contents('openai')
            print("✅ Configuration file loaded successfully")
            
            # Validate required fields
            required_fields = ['token_url', 'client_id', 'client_secret', 'app_key']
            missing_fields = [field for field in required_fields if not config.get(field)]
            
            if missing_fields:
                print(f"❌ Missing required fields: {missing_fields}")
                return False
            else:
                print("✅ All required configuration fields present")
                
        except Exception as e:
            print(f"❌ Configuration loading failed: {str(e)}")
            return False
        
        # Test client initialization
        print("\n2. Testing client initialization...")
        try:
            client = CiscoOpenAIClient()
            print("✅ Cisco OpenAI client initialized")
        except Exception as e:
            print(f"❌ Client initialization failed: {str(e)}")
            return False
        
        # Test token generation
        print("\n3. Testing OAuth token generation...")
        try:
            token = client._get_openai_token()
            if token:
                print(f"✅ OAuth token generated successfully: {token[:10]}...{token[-4:]}")
            else:
                print("❌ Token generation returned empty token")
                return False
        except Exception as e:
            print(f"❌ Token generation failed: {str(e)}")
            return False
        
        # Test API availability
        print("\n4. Testing API availability...")
        try:
            if client.is_available():
                print("✅ Cisco OpenAI API is available")
            else:
                print("❌ Cisco OpenAI API is not available")
                return False
        except Exception as e:
            print(f"❌ API availability check failed: {str(e)}")
            return False
        
        # Test actual API call
        print("\n5. Testing API call...")
        try:
            from utils.llm_client import LLMMessage
            test_messages = [LLMMessage("user", "Hello, this is a test message.")]
            
            response = client.generate_response(test_messages)
            if response:
                print(f"✅ API call successful! Response: {response[:100]}...")
                return True
            else:
                print("❌ API call returned empty response")
                return False
                
        except Exception as e:
            print(f"❌ API call failed: {str(e)}")
            return False
            
    except ImportError as e:
        print(f"❌ Import error: {str(e)}")
        print("Make sure all dependencies are installed: pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False

def print_configuration_help():
    """Print help for configuring Cisco OpenAI."""
    print("\n📋 Configuration Help")
    print("=" * 30)
    print("To set up Cisco Enterprise OpenAI, you need:")
    print("\n1. Create config/openai.properties with:")
    print("   [openai]")
    print("   token_url=https://your-auth-server.cisco.com/oauth2/token")
    print("   client_id=your_client_id")
    print("   client_secret=your_client_secret") 
    print("   grant_type=client_credentials")
    print("   app_key=your_app_key")
    print("   azure_endpoint=https://chat-ai.cisco.com")
    print("   api_version=2024-07-01-preview")
    print("\n2. OR set environment variables:")
    print("   CISCO_OPENAI_TOKEN_URL=...")
    print("   CISCO_OPENAI_CLIENT_ID=...")
    print("   CISCO_OPENAI_CLIENT_SECRET=...")
    print("   CISCO_OPENAI_APP_KEY=...")
    print("\n3. Contact your Cisco IT administrator for the actual values.")

def main():
    """Main test function."""
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print_configuration_help()
        return
    
    success = test_cisco_openai_config()
    
    if success:
        print("\n🎉 Cisco Enterprise OpenAI is fully configured and working!")
        print("You can now use the multi-agent system with your enterprise setup.")
        print("\nNext steps:")
        print("1. Set DEMO_MODE=false in your .env file")
        print("2. Run: python main.py --query 'Hello from Cisco OpenAI'")
    else:
        print("\n❌ Cisco Enterprise OpenAI configuration has issues.")
        print("\nTroubleshooting:")
        print("1. Verify your configuration file exists and has correct values")
        print("2. Check your network connectivity to Cisco endpoints")
        print("3. Verify your OAuth credentials with your IT administrator")
        print("4. Run with --help for configuration guidance")

if __name__ == "__main__":
    main()
