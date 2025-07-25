# GitHub MCP Server

A Model Context Protoc2. Set up configuration:
```bash
cp config/config.example.ini config/config.ini
# Edit config/config.ini with your GitHub App credentials
```CP) server for GitHub integration using GitHub App authentication, built with **FastAPI** and **FastMCP**.

## Features

- **FastMCP Integration**: Built using FastMCP for efficient MCP protocol handling
- **GitHub App Authentication**: Secure authentication using GitHub App with private key
- **Webhook Endpoints**: Handle GitHub webhooks for real-time event processing
- **GitHub Actions Integration**: Interact with GitHub Actions workflows
- **Wiki Operations**: Create, update, and delete GitHub wiki pages
- **Repository Management**: Comprehensive repository operations
- **Issue and PR Management**: Handle issues and pull requests

## Setup

### Prerequisites

- Python 3.9+
- GitHub App with appropriate permissions
- Private key file for GitHub App authentication

### Installation

#### Option 1: Local Development

1. Clone the repository:
```bash
git clone <repository-url>
cd github-mcp-server
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -e .
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your GitHub App credentials
```

#### Option 2: Docker (Recommended)

1. Clone the repository:
```bash
git clone <repository-url>
cd github-mcp-server
```

2. Set up configuration:
```bash
cp config/config.example.ini config/config.ini
# Edit config/config.ini with your GitHub App credentials
```

3. Build and run with Docker:
```bash
# Using the provided script
./docker.sh build
./docker.sh run

# Or using Docker directly
docker build -t github-mcp-server .
docker run -p 8000:8000 \
  -v "$(pwd)/config/config.ini:/app/config/config.ini:ro" \
  -v "$(pwd)/gitdocbot.private-key.pem:/app/gitdocbot.private-key.pem:ro" \
  github-mcp-server

# Or using Docker Compose
docker-compose up -d
```

### Configuration

Create a `config/config.ini` file with your GitHub App credentials:

```ini
[github]
app_id = 1656559
private_key_path = gitdocbot.private-key.pem
webhook_secret = your_webhook_secret

[server]
host = 0.0.0.0
port = 8000
```

You can copy from the example configuration:
```bash
cp config/config.example.ini config/config.ini
# Edit config/config.ini with your credentials
```

## Running the Server

### Local Development
```bash
uvicorn github_mcp_server.main:app --reload --host 0.0.0.0 --port 8000
```

### Docker
```bash
# Quick start
./docker.sh compose

# Manual Docker commands
docker build -t github-mcp-server .
docker run -p 8000:8000 --env-file .env github-mcp-server

# Check status
./docker.sh status

# View logs
./docker.sh logs
```

### Production with Docker Compose + Nginx
```bash
# Run with reverse proxy
docker-compose --profile production up -d
```

## MCP Integration

The server uses **FastAPI-MCP** for native MCP protocol integration. FastAPI-MCP automatically exposes all the defined tools as MCP endpoints and handles the MCP protocol details.

### MCP Client Configuration

Add this to your MCP client configuration:

```json
{
  "servers": {
    "github-mcp-server": {
      "type": "http",
      "url": "http://localhost:8000"
    }
  }
}
```

### Available MCP Tools

FastAPI-MCP automatically exposes the following tools via the MCP protocol:

- `create_repo` - Create a new GitHub repository
- `get_repo_info` - Get repository information  
- `create_issue` - Create a new issue
- `update_issue` - Update an existing issue
- `create_pull_request` - Create a new pull request
- `merge_pull_request` - Merge a pull request
- `create_wiki_page` - Create a wiki page
- `update_wiki_page` - Update a wiki page
- `delete_wiki_page` - Delete a wiki page
- `trigger_workflow` - Trigger a GitHub Actions workflow

### Direct Tool Access

You can also access tools directly via HTTP endpoints:

```bash
# List all available tools (via OpenAPI)
curl http://localhost:8000/docs

# Call a tool directly
curl -X POST http://localhost:8000/tools/get_repo_info \
  -H "Content-Type: application/json" \
  -d '{
    "owner": "username",
    "name": "repository"
  }'
```

## API Endpoints

### Core Endpoints
- `GET /health` - Health check endpoint
- `GET /docs` - OpenAPI documentation (Swagger UI)
- `GET /openapi.json` - OpenAPI specification

### GitHub Tools (via FastAPI-MCP)
- `POST /tools/create_repo` - Create a new GitHub repository
- `POST /tools/get_repo_info` - Get repository information
- `POST /tools/create_issue` - Create a new issue
- `POST /tools/update_issue` - Update an existing issue
- `POST /tools/create_pull_request` - Create a new pull request
- `POST /tools/merge_pull_request` - Merge a pull request
- `POST /tools/create_wiki_page` - Create a wiki page
- `POST /tools/update_wiki_page` - Update a wiki page
- `POST /tools/delete_wiki_page` - Delete a wiki page
- `POST /tools/trigger_workflow` - Trigger a GitHub Actions workflow

### GitHub Actions API
- `POST /actions/{owner}/{repo}/dispatch` - Trigger workflow dispatch
- `GET /actions/{owner}/{repo}/workflows` - List repository workflows
- `GET /actions/{owner}/{repo}/workflows/{workflow_id}/runs` - List workflow runs

### Webhooks
- `POST /webhooks/github` - GitHub webhook handler

## Tools Available

The following tools are automatically exposed via FastAPI-MCP:

- `create_repo` - Create a new GitHub repository
- `get_repo_info` - Get repository information
- `create_issue` - Create a new issue
- `update_issue` - Update an existing issue
- `create_pull_request` - Create a new pull request
- `merge_pull_request` - Merge a pull request
- `create_wiki_page` - Create a wiki page
- `update_wiki_page` - Update a wiki page
- `delete_wiki_page` - Delete a wiki page
- `trigger_workflow` - Trigger a GitHub Actions workflow

All tools support optional `installation_id` parameter for GitHub App installations.

## License

MIT License

## Docker Management

The project includes a convenient Docker management script (`docker.sh`) with the following commands:

```bash
# Build the Docker image
./docker.sh build

# Run with Docker (single container)
./docker.sh run

# Run with Docker Compose
./docker.sh compose

# Stop all containers
./docker.sh stop

# Show container logs
./docker.sh logs

# Check status and health
./docker.sh status

# Clean up Docker resources
./docker.sh clean

# Show help
./docker.sh help
```

### Docker Environment

The Docker setup uses configuration from `config/config.ini` instead of environment variables. Make sure to:

1. Copy the example configuration: `cp config/config.example.ini config/config.ini`
2. Edit `config/config.ini` with your GitHub App credentials
3. Ensure your private key file is in the project root
