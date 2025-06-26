# API Tokens Required for LangGraph Multi-Agent System

This guide provides information about the API tokens needed to run the multi-agent system without demo mode.

## Required API Tokens

### 1. LLM Provider APIs (Choose at least one)

#### Cisco Enterprise OpenAI (Enterprise Users)
- **Token Name**: Configuration file or environment variables
- **Purpose**: Enterprise-grade OpenAI access through Cisco's OAuth system
- **How to get it**:
  1. Contact your Cisco IT administrator for credentials
  2. Obtain: `client_id`, `client_secret`, `token_url`, `app_key`
  3. Create `config/openai.properties` file (see below)
- **Cost**: Depends on your enterprise agreement
- **Models supported**: Standard OpenAI models through Azure endpoint

#### OpenAI API (Public)
- **Token Name**: `OPENAI_API_KEY`
- **Purpose**: Powers the language models for all agents (GPT-4, GPT-3.5, etc.)
- **How to get it**:
  1. Go to [OpenAI Platform](https://platform.openai.com)
  2. Sign up or log in to your account
  3. Navigate to [API Keys](https://platform.openai.com/api-keys)
  4. Click "Create new secret key"
  5. Copy the key and add it to your `.env` file
- **Cost**: Pay-per-use, typically $0.01-0.06 per 1K tokens depending on model
- **Models supported**: 
  - `gpt-4o-mini` (recommended for cost efficiency)
  - `gpt-4o` (higher quality, more expensive)
  - `gpt-3.5-turbo` (legacy, cheaper)

#### Anthropic API (Alternative)
- **Token Name**: `ANTHROPIC_API_KEY`
- **Purpose**: Alternative LLM provider using Claude models
- **How to get it**:
  1. Go to [Anthropic Console](https://console.anthropic.com)
  2. Sign up or log in to your account
  3. Navigate to [API Keys](https://console.anthropic.com/settings/keys)
  4. Click "Create Key"
  5. Copy the key and add it to your `.env` file
- **Cost**: Pay-per-use, competitive pricing with OpenAI
- **Models supported**:
  - `claude-3-5-sonnet-20241022` (recommended)
  - `claude-3-haiku-20240307` (faster, cheaper)

## Optional API Tokens (For Enhanced Functionality)

### 2. Search and Research APIs

#### Tavily Search API (Web Search)
- **Token Name**: `TAVILY_API_KEY`
- **Purpose**: Powers web search capabilities for research agent
- **How to get it**:
  1. Go to [Tavily](https://tavily.com)
  2. Sign up for an account
  3. Navigate to your dashboard
  4. Copy your API key
- **Cost**: Free tier available, then pay-per-search

#### SerpAPI (Alternative Search)
- **Token Name**: `SERPAPI_KEY`
- **Purpose**: Alternative search API for research
- **How to get it**:
  1. Go to [SerpAPI](https://serpapi.com)
  2. Sign up for an account
  3. Get your API key from dashboard
- **Cost**: Free tier with limited searches

### 3. Code Execution APIs

#### CodeAPI or Replit API
- **Token Name**: `CODE_EXECUTION_API_KEY`
- **Purpose**: Safe code execution in sandboxed environments
- **How to get it**:
  1. Go to [Replit](https://replit.com) or similar service
  2. Sign up and get API access
- **Cost**: Free tier available

### 4. File and Data APIs

#### GitHub API (Optional)
- **Token Name**: `GITHUB_TOKEN`
- **Purpose**: Access repositories, read code files
- **How to get it**:
  1. Go to [GitHub Settings](https://github.com/settings/tokens)
  2. Generate a new personal access token
  3. Select appropriate scopes
- **Cost**: Free for public repositories

## Setting Up Your Environment

### Step 1: Copy Environment File
```bash
cp .env.example .env
```

### Step 2: Edit Your .env File
Open `.env` and replace the placeholder values:

```bash
# Required: Choose at least one
OPENAI_API_KEY=sk-your-actual-openai-key-here
# ANTHROPIC_API_KEY=your-actual-anthropic-key-here

# Turn off demo mode
DEMO_MODE=false

# Optional: Specify preferred model
DEFAULT_MODEL=gpt-4o-mini

# Optional: Additional APIs
# TAVILY_API_KEY=your-tavily-key-here
# GITHUB_TOKEN=your-github-token-here
```

### Step 3: Test Your Configuration
```bash
python main.py --query "Hello, test my API configuration"
```

## Cost Estimation

### Minimal Setup (OpenAI only)
- **Initial cost**: $5-10 credit should last for hundreds of queries
- **Per query**: Approximately $0.01-0.05 depending on complexity
- **Monthly usage** (moderate): $10-30

### Enhanced Setup (All APIs)
- **OpenAI**: $10-30/month
- **Search APIs**: $5-15/month
- **Total**: $15-45/month

## Security Best Practices

1. **Never commit API keys to version control**
2. **Use environment variables only**
3. **Rotate keys regularly**
4. **Set up billing alerts**
5. **Use least-privilege API scopes**

## Troubleshooting

### Common Issues

1. **"No LLM provider available"**
   - Check that at least one API key is set correctly
   - Verify the key format (OpenAI keys start with `sk-`)

2. **"Rate limit exceeded"**
   - OpenAI: Check your usage limits in dashboard
   - Consider upgrading your plan or using slower requests

3. **"Invalid API key"**
   - Double-check the key was copied correctly
   - Ensure no extra spaces or characters

### Testing Individual APIs

```bash
# Test OpenAI connection
python -c "
import os
from openai import OpenAI
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
print('OpenAI connection successful')
"

# Test Anthropic connection
python -c "
import os
from anthropic import Anthropic
client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
print('Anthropic connection successful')
"
```

## Quick Start Checklist

- [ ] Get OpenAI API key from platform.openai.com
- [ ] Copy `.env.example` to `.env`
- [ ] Add your OpenAI API key to `.env`
- [ ] Set `DEMO_MODE=false`
- [ ] Run `python main.py --query "test"`
- [ ] Verify system works without demo mode
- [ ] (Optional) Add additional API keys for enhanced features

## Support

If you encounter issues:
1. Check the troubleshooting section above
2. Verify your API keys are correctly formatted
3. Check the service status pages for the APIs you're using
4. Review the application logs for specific error messages

---

**Note**: Start with just the OpenAI API key for basic functionality. You can add other APIs later as needed.

## Cisco Enterprise OpenAI Configuration

### Configuration File Method (Recommended)

Create `config/openai.properties`:
```ini
[openai]
token_url=https://your-auth-server.cisco.com/oauth2/token
client_id=your_client_id_here
client_secret=your_client_secret_here
grant_type=client_credentials
app_key=your_app_key_here
azure_endpoint=https://chat-ai.cisco.com
api_version=2024-07-01-preview
model=gpt-4o-mini
```

### Environment Variables Method

Set these environment variables:
```bash
CISCO_OPENAI_TOKEN_URL=https://your-auth-server.cisco.com/oauth2/token
CISCO_OPENAI_CLIENT_ID=your_client_id_here
CISCO_OPENAI_CLIENT_SECRET=your_client_secret_here
CISCO_OPENAI_GRANT_TYPE=client_credentials
CISCO_OPENAI_APP_KEY=your_app_key_here
CISCO_OPENAI_AZURE_ENDPOINT=https://chat-ai.cisco.com
CISCO_OPENAI_API_VERSION=2024-07-01-preview
CISCO_OPENAI_MODEL=gpt-4o-mini

# Set provider preference
LLM_PROVIDER=cisco_openai
DEMO_MODE=false
```
