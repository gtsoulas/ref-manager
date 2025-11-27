#!/bin/bash

# REF-Manager Multi-User Setup Wizard
# Guides you through choosing and setting up the best deployment method

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

clear

echo "=========================================="
echo -e "${BLUE}REF-Manager Multi-User Setup Wizard${NC}"
echo "=========================================="
echo ""
echo "This wizard will help you set up REF-Manager"
echo "for multiple simultaneous users."
echo ""

# Check if in correct directory
if [ ! -f "manage.py" ]; then
    echo -e "${RED}❌ ERROR: Not in REF-manager directory${NC}"
    echo "Please run this from: ~/REF-Stuff/ref-manager/"
    exit 1
fi

echo -e "${GREEN}✅ Found REF-manager project${NC}"
echo ""

# Step 1: Choose deployment method
echo "=========================================="
echo "Step 1: Choose Deployment Method"
echo "=========================================="
echo ""
echo "Choose how you want to deploy REF-Manager:"
echo ""
echo "  1) Docker (Recommended)"
echo "     • Fastest setup (~15 minutes)"
echo "     • Everything in containers"
echo "     • Easy to update and maintain"
echo "     • Great for most users"
echo ""
echo "  2) Standard (Traditional Server)"
echo "     • Full control (~30-45 minutes)"
echo "     • Native system services"
echo "     • Better for integration with existing infrastructure"
echo "     • Good if you're experienced with Linux servers"
echo ""
echo "  3) Exit and read documentation first"
echo ""
read -p "Enter your choice (1, 2, or 3): " DEPLOYMENT_CHOICE

case $DEPLOYMENT_CHOICE in
    1)
        echo ""
        echo -e "${BLUE}Docker Deployment Selected${NC}"
        DEPLOYMENT="docker"
        ;;
    2)
        echo ""
        echo -e "${BLUE}Standard Deployment Selected${NC}"
        DEPLOYMENT="standard"
        ;;
    3)
        echo ""
        echo "Please read MASTER_INSTALLATION_GUIDE.md first"
        exit 0
        ;;
    *)
        echo -e "${RED}Invalid choice${NC}"
        exit 1
        ;;
esac

echo ""
echo "=========================================="
echo "Step 2: Prerequisites Check"
echo "=========================================="
echo ""

if [ "$DEPLOYMENT" = "docker" ]; then
    # Check Docker
    if command -v docker &> /dev/null; then
        echo -e "${GREEN}✅ Docker installed${NC}"
    else
        echo -e "${YELLOW}⚠️  Docker not found${NC}"
        echo ""
        read -p "Install Docker now? (yes/no): " INSTALL_DOCKER
        if [ "$INSTALL_DOCKER" = "yes" ]; then
            echo "Installing Docker..."
            curl -fsSL https://get.docker.com -o get-docker.sh
            sudo sh get-docker.sh
            sudo usermod -aG docker $USER
            echo -e "${GREEN}✅ Docker installed${NC}"
            echo -e "${YELLOW}⚠️  You need to log out and back in for Docker permissions${NC}"
            echo "Run this script again after logging back in."
            exit 0
        else
            echo "Please install Docker first: https://docs.docker.com/get-docker/"
            exit 1
        fi
    fi
    
    # Check Docker Compose
    if command -v docker compose &> /dev/null || docker compose version &> /dev/null; then
        echo -e "${GREEN}✅ Docker Compose installed${NC}"
    else
        echo -e "${YELLOW}⚠️  Docker Compose not found${NC}"
        echo "Installing Docker Compose..."
        sudo apt-get update
        sudo apt-get install -y docker-compose-plugin
        echo -e "${GREEN}✅ Docker Compose installed${NC}"
    fi
    
else
    # Check PostgreSQL
    if command -v psql &> /dev/null; then
        echo -e "${GREEN}✅ PostgreSQL installed${NC}"
    else
        echo -e "${YELLOW}⚠️  PostgreSQL not found${NC}"
        echo ""
        read -p "Install PostgreSQL now? (yes/no): " INSTALL_PG
        if [ "$INSTALL_PG" = "yes" ]; then
            echo "Installing PostgreSQL..."
            sudo apt-get update
            sudo apt-get install -y postgresql postgresql-contrib libpq-dev
            echo -e "${GREEN}✅ PostgreSQL installed${NC}"
        else
            echo "Please install PostgreSQL first"
            exit 1
        fi
    fi
    
    # Check Nginx
    if command -v nginx &> /dev/null; then
        echo -e "${GREEN}✅ Nginx installed${NC}"
    else
        echo -e "${YELLOW}⚠️  Nginx not found${NC}"
        echo ""
        read -p "Install Nginx now? (yes/no): " INSTALL_NGINX
        if [ "$INSTALL_NGINX" = "yes" ]; then
            echo "Installing Nginx..."
            sudo apt-get install -y nginx
            echo -e "${GREEN}✅ Nginx installed${NC}"
        else
            echo "Nginx will be needed for production deployment"
        fi
    fi
fi

echo ""
echo "=========================================="
echo "Step 3: Deployment Setup"
echo "=========================================="
echo ""

if [ "$DEPLOYMENT" = "docker" ]; then
    echo "Setting up Docker deployment..."
    echo ""
    
    # Check if Docker files exist
    if [ ! -f "Dockerfile" ]; then
        echo -e "${YELLOW}⚠️  Docker configuration files not found${NC}"
        echo ""
        echo "Please copy these files to your project:"
        echo "  • Dockerfile"
        echo "  • docker-compose.yml"
        echo "  • .dockerignore"
        echo "  • nginx.conf"
        echo ""
        echo "From the deployment package provided."
        echo ""
        read -p "Have you copied these files? (yes/no): " FILES_COPIED
        if [ "$FILES_COPIED" != "yes" ]; then
            echo "Please copy the files first, then run this wizard again."
            exit 1
        fi
    fi
    
    # Setup directories
    echo "Creating required directories..."
    mkdir -p nginx/conf.d nginx/ssl logs/nginx backups
    
    # Copy nginx config if needed
    if [ -f "nginx.conf" ] && [ ! -f "nginx/conf.d/ref-manager.conf" ]; then
        cp nginx.conf nginx/conf.d/ref-manager.conf
        echo -e "${GREEN}✅ Nginx configuration copied${NC}"
    fi
    
    # Create .env file
    if [ ! -f ".env" ]; then
        echo ""
        echo "Creating environment configuration..."
        
        # Generate secret key
        SECRET_KEY=$(python3 -c 'import random, string; print("".join(random.choices(string.ascii_letters + string.digits + string.punctuation, k=50)))' 2>/dev/null || openssl rand -base64 32)
        
        # Get database password
        echo ""
        read -s -p "Enter a strong password for the database: " DB_PASS
        echo ""
        read -s -p "Confirm password: " DB_PASS_CONFIRM
        echo ""
        
        if [ "$DB_PASS" != "$DB_PASS_CONFIRM" ]; then
            echo -e "${RED}Passwords don't match${NC}"
            exit 1
        fi
        
        # Get allowed hosts
        echo ""
        echo "Enter allowed hosts (comma-separated):"
        echo "Examples:"
        echo "  localhost,127.0.0.1"
        echo "  localhost,127.0.0.1,192.168.1.100"
        echo "  localhost,127.0.0.1,ref-manager.york.ac.uk"
        read -p "Allowed hosts: " ALLOWED_HOSTS
        
        # Create .env file
        cat > .env <<EOF
# REF-Manager Environment Configuration
# Generated by setup wizard on $(date)

DB_PASSWORD=$DB_PASS
SECRET_KEY=$SECRET_KEY
DEBUG=False
ALLOWED_HOSTS=${ALLOWED_HOSTS:-localhost,127.0.0.1}

# Database
DB_ENGINE=postgresql
DB_NAME=ref_manager_db
DB_USER=ref_manager_user
DB_HOST=db
DB_PORT=5432
EOF
        
        echo -e "${GREEN}✅ Environment file created${NC}"
    else
        echo -e "${YELLOW}⚠️  .env file already exists${NC}"
    fi
    
    # Start services
    echo ""
    read -p "Start Docker services now? (yes/no): " START_NOW
    if [ "$START_NOW" = "yes" ]; then
        echo ""
        echo "Starting services..."
        docker compose up -d
        
        echo ""
        echo "Waiting for services to be ready..."
        sleep 10
        
        echo ""
        docker compose ps
        
        echo ""
        echo -e "${GREEN}✅ Services started${NC}"
        echo ""
        echo "Create an admin user:"
        docker compose exec web python manage.py createsuperuser
        
        echo ""
        echo -e "${GREEN}=========================================="
        echo "✅ Docker Deployment Complete!"
        echo "==========================================${NC}"
        echo ""
        echo "Access REF-Manager at:"
        echo "  • Application: http://localhost"
        echo "  • Admin: http://localhost/admin"
        echo ""
        echo "Useful commands:"
        echo "  • View logs: docker compose logs -f"
        echo "  • Stop: docker compose down"
        echo "  • Restart: docker compose restart"
        echo ""
        echo "Full documentation: DOCKER_DEPLOYMENT_GUIDE.md"
    fi
    
else
    # Standard deployment
    echo "Starting PostgreSQL migration..."
    echo ""
    
    if [ -f "migrate_to_postgresql.sh" ]; then
        bash migrate_to_postgresql.sh
        
        echo ""
        echo -e "${GREEN}=========================================="
        echo "✅ PostgreSQL Migration Complete!"
        echo "==========================================${NC}"
        echo ""
        echo "Next steps:"
        echo ""
        echo "1. Set up Gunicorn and Nginx:"
        echo "   Follow: DEPLOYMENT_GUIDE.md"
        echo ""
        echo "2. Configure systemd service"
        echo "3. Enable SSL/HTTPS"
        echo "4. Set up automated backups"
        echo ""
        echo "Estimated time: 30-45 minutes"
        echo ""
        echo "Start now? The guide will walk you through each step."
        read -p "(yes/no): " START_DEPLOYMENT
        
        if [ "$START_DEPLOYMENT" = "yes" ]; then
            echo ""
            echo "Opening deployment guide..."
            less DEPLOYMENT_GUIDE.md
        fi
    else
        echo -e "${RED}Migration script not found${NC}"
        echo "Please ensure migrate_to_postgresql.sh is in your project directory"
        exit 1
    fi
fi

echo ""
echo -e "${BLUE}=========================================="
echo "Setup Wizard Complete"
echo "==========================================${NC}"
echo ""
echo "Thank you for setting up REF-Manager!"
echo ""
