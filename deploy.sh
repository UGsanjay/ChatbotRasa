#!/bin/bash

echo "🚀 Mempersiapkan deployment Rasa Chatbot ke Railway..."

# Warna untuk output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo -e "${YELLOW}📁 Initializing Git repository...${NC}"
    git init
fi

# Create necessary files if they don't exist
echo -e "${YELLOW}📝 Checking required files...${NC}"

# Create Dockerfile
if [ ! -f "Dockerfile" ]; then
    echo -e "${GREEN}✅ Creating Dockerfile...${NC}"
    cat > Dockerfile << 'EOF'
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    default-mysql-client \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all files
COPY . .

# Train model if not exists
RUN if [ ! -d "models" ] || [ -z "$(ls -A models)" ]; then rasa train --fixed-model-name model; fi

# Expose port
EXPOSE $PORT

# Start Rasa server
CMD rasa run --enable-api --cors "*" --port $PORT --host 0.0.0.0
EOF
fi

# Create requirements.txt if doesn't exist
if [ ! -f "requirements.txt" ]; then
    echo -e "${GREEN}✅ Creating requirements.txt...${NC}"
    cat > requirements.txt << 'EOF'
rasa>=3.6.0
rasa-sdk>=3.6.0
pymysql>=1.0.2
python-dotenv>=1.0.0
requests>=2.28.0
EOF
fi

# Create railway.toml
if [ ! -f "railway.toml" ]; then
    echo -e "${GREEN}✅ Creating railway.toml...${NC}"
    cat > railway.toml << 'EOF'
[build]
builder = "dockerfile"

[deploy]
healthcheckPath = "/"
healthcheckTimeout = 100
restartPolicyType = "always"
EOF
fi

# Create .gitignore
if [ ! -f ".gitignore" ]; then
    echo -e "${GREEN}✅ Creating .gitignore...${NC}"
    cat > .gitignore << 'EOF'
# Environment files
.env
.env.local
.env.production

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
pip-wheel-metadata/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Rasa
.rasa/
EOF
fi

# Check if model exists
if [ ! -d "models" ] || [ -z "$(ls -A models 2>/dev/null)" ]; then
    echo -e "${YELLOW}🤖 No trained model found. Training model...${NC}"
    if command -v rasa &> /dev/null; then
        rasa train --fixed-model-name model
        echo -e "${GREEN}✅ Model trained successfully!${NC}"
    else
        echo -e "${RED}❌ Rasa not found. Please install Rasa first or ensure you have a trained model.${NC}"
        exit 1
    fi
fi

# Add all files to git
echo -e "${YELLOW}📦 Adding files to git...${NC}"
git add .

# Check if there are changes to commit
if git diff --staged --quiet; then
    echo -e "${YELLOW}⚠️  No changes to commit.${NC}"
else
    # Commit changes
    echo -e "${YELLOW}💾 Committing changes...${NC}"
    git commit -m "Prepare for Railway deployment - $(date)"
fi

echo -e "${GREEN}🎉 Preparation complete!${NC}"
echo ""
echo -e "${YELLOW}📋 Next steps:${NC}"
echo "1. Create a GitHub repository"
echo "2. Push your code:"
echo "   ${GREEN}git remote add origin https://github.com/UGsanjay/ChatbotRasa.git${NC}"
echo "   ${GREEN}git branch -M main${NC}"
echo "   ${GREEN}git push -u origin main${NC}"
echo ""
echo "3. Go to Railway.app and:"
echo "   - Create new project from GitHub repo"
echo "   - Add environment variables:"
echo "     ${GREEN}PORT=5005${NC}"
echo "     ${GREEN}MYSQL_HOST=your_mysql_host${NC}"
echo "     ${GREEN}MYSQL_PORT=3306${NC}"
echo "     ${GREEN}MYSQL_USER=your_mysql_user${NC}"
echo "     ${GREEN}MYSQL_PASSWORD=your_mysql_password${NC}"
echo "     ${GREEN}MYSQL_DATABASE=your_database_name${NC}"
echo ""
echo -e "${GREEN}🚀 Your chatbot will be live at: https://PI_51422509.up.railway.app${NC}"