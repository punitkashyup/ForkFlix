#!/bin/bash

# ForkFlix Deployment Script
# This script helps deploy the ForkFlix application using Docker

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
}

# Check if Firebase credentials exist
check_firebase() {
    if [ ! -f "./firebase/firebase-admin-key.json" ]; then
        print_error "Firebase admin key not found at ./firebase/firebase-admin-key.json"
        print_error "Please ensure you have the Firebase service account key file in the correct location."
        exit 1
    fi
    print_status "Firebase credentials found."
}

# Function to build images
build_images() {
    print_status "Building Docker images..."
    docker-compose build --no-cache
    print_status "Images built successfully."
}

# Function to start services
start_services() {
    print_status "Starting services..."
    docker-compose up -d
    print_status "Services started successfully."
}

# Function to stop services
stop_services() {
    print_status "Stopping services..."
    docker-compose down
    print_status "Services stopped successfully."
}

# Function to show logs
show_logs() {
    local service=${1:-""}
    if [ -n "$service" ]; then
        docker-compose logs -f "$service"
    else
        docker-compose logs -f
    fi
}

# Function to show status
show_status() {
    print_status "Service status:"
    docker-compose ps
    echo
    print_status "Application URLs:"
    echo "Frontend: http://localhost:80"
    echo "Backend API: http://localhost:8000"
    echo "Backend Health: http://localhost:8000/health"
}

# Function to clean up
cleanup() {
    print_warning "Cleaning up..."
    docker-compose down -v --remove-orphans
    docker system prune -f
    print_status "Cleanup completed."
}

# Function to deploy for production
deploy_production() {
    print_status "Deploying for production..."
    docker-compose -f docker-compose.prod.yml up -d --build
    print_status "Production deployment completed."
}

# Main menu
main() {
    echo "========================================="
    echo "         ForkFlix Deployment"
    echo "========================================="
    echo
    
    case "${1:-}" in
        "build")
            check_docker
            check_firebase
            build_images
            ;;
        "start")
            check_docker
            check_firebase
            start_services
            show_status
            ;;
        "stop")
            stop_services
            ;;
        "restart")
            check_docker
            check_firebase
            stop_services
            start_services
            show_status
            ;;
        "logs")
            show_logs "${2:-}"
            ;;
        "status")
            show_status
            ;;
        "cleanup")
            cleanup
            ;;
        "prod")
            check_docker
            check_firebase
            deploy_production
            show_status
            ;;
        "dev")
            check_docker
            check_firebase
            print_status "Starting development environment..."
            docker-compose up --build
            ;;
        *)
            echo "Usage: $0 {build|start|stop|restart|logs|status|cleanup|prod|dev}"
            echo
            echo "Commands:"
            echo "  build    - Build Docker images"
            echo "  start    - Start services in detached mode"
            echo "  stop     - Stop all services"
            echo "  restart  - Restart all services"
            echo "  logs     - Show logs (optional: specify service name)"
            echo "  status   - Show service status and URLs"
            echo "  cleanup  - Stop services and clean up Docker resources"
            echo "  prod     - Deploy for production"
            echo "  dev      - Start development environment with logs"
            echo
            echo "Examples:"
            echo "  $0 start"
            echo "  $0 logs backend"
            echo "  $0 prod"
            exit 1
            ;;
    esac
}

main "$@"