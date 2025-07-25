#!/bin/bash

# GitHub MCP Server Docker Management Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if config.ini file exists
check_config() {
    if [ ! -f config/config.ini ]; then
        print_warning "config.ini file not found. Creating from config.example.ini..."
        cp config/config.example.ini config/config.ini
        print_warning "Please edit config/config.ini file with your GitHub App credentials"
    fi
}

# Check if private key exists
check_private_key() {
    if [ ! -f gitdocbot.private-key.pem ]; then
        print_error "Private key file 'gitdocbot.private-key.pem' not found!"
        print_error "Please ensure your GitHub App private key is in the project root."
        exit 1
    fi
}

# Build Docker image
build() {
    print_status "Building GitHub MCP Server Docker image with uv..."
    docker build -t github-mcp-server:latest .
    print_status "Build completed successfully!"
}

# Run with Docker
run() {
    check_config
    check_private_key
    
    print_status "Starting GitHub MCP Server..."
    docker run -d \
        --name github-mcp-server \
        -p 8000:8000 \
        -v "$(pwd)/config/config.ini:/app/config/config.ini:ro" \
        -v "$(pwd)/gitdocbot.private-key.pem:/app/gitdocbot.private-key.pem:ro" \
        github-mcp-server:latest
    
    print_status "Server started! Available at http://localhost:8000"
    print_status "Health check: http://localhost:8000/health"
    print_status "MCP endpoints: http://localhost:8000/mcp/"
}

# Run with docker-compose
run_compose() {
    check_config
    check_private_key
    
    print_status "Starting GitHub MCP Server with Docker Compose..."
    docker-compose up -d
    print_status "Server started! Available at http://localhost:8000"
}

# Stop containers
stop() {
    print_status "Stopping GitHub MCP Server..."
    docker stop github-mcp-server 2>/dev/null || true
    docker rm github-mcp-server 2>/dev/null || true
    docker-compose down 2>/dev/null || true
    print_status "Server stopped!"
}

# Show logs
logs() {
    if docker ps | grep -q github-mcp-server; then
        docker logs -f github-mcp-server
    elif docker-compose ps | grep -q github-mcp-server; then
        docker-compose logs -f github-mcp-server
    else
        print_error "No running GitHub MCP Server container found!"
        exit 1
    fi
}

# Show status
status() {
    echo "=== Docker Container Status ==="
    docker ps -a | grep github-mcp-server || echo "No containers found"
    
    echo -e "\n=== Docker Compose Status ==="
    docker-compose ps 2>/dev/null || echo "Docker Compose not running"
    
    echo -e "\n=== Health Check ==="
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        print_status "Server is healthy!"
        curl -s http://localhost:8000/health | jq . 2>/dev/null || curl -s http://localhost:8000/health
    else
        print_warning "Server is not responding on http://localhost:8000"
    fi
}

# Clean up
clean() {
    print_status "Cleaning up Docker resources..."
    stop
    docker rmi github-mcp-server:latest 2>/dev/null || true
    docker system prune -f
    print_status "Cleanup completed!"
}

# Show help
help() {
    echo "GitHub MCP Server Docker Management"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  build       Build the Docker image"
    echo "  run         Run with Docker (single container)"
    echo "  compose     Run with Docker Compose"
    echo "  stop        Stop all containers"
    echo "  logs        Show container logs"
    echo "  status      Show status and health check"
    echo "  clean       Clean up Docker resources"
    echo "  help        Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 build && $0 run"
    echo "  $0 compose"
    echo "  $0 status"
}

# Main script logic
case "${1:-help}" in
    build)
        build
        ;;
    run)
        build
        run
        ;;
    compose)
        build
        run_compose
        ;;
    stop)
        stop
        ;;
    logs)
        logs
        ;;
    status)
        status
        ;;
    clean)
        clean
        ;;
    help|*)
        help
        ;;
esac
