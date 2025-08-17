#!/bin/bash

# Serbian Vocabulary Bot - Quick Setup Script
# This script helps you set up the development environment quickly

set -e

echo "🇷🇸 Serbian Vocabulary Learning Bot - Quick Setup"
echo "=================================================="

# Check if required tools are installed
echo "📋 Checking prerequisites..."

command -v docker >/dev/null 2>&1 || { echo "❌ Docker is required but not installed. Please install Docker first."; exit 1; }
command -v docker-compose >/dev/null 2>&1 || command -v docker >/dev/null 2>&1 || { echo "❌ Docker Compose is required but not installed."; exit 1; }
command -v git >/dev/null 2>&1 || { echo "❌ Git is required but not installed."; exit 1; }

echo "✅ All prerequisites found!"

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    if [ -f .env.example ]; then
        cp .env.example .env
        echo "✅ .env file created from .env.example"
    else
        echo "❌ .env.example not found. Please create .env manually."
        exit 1
    fi
else
    echo "✅ .env file already exists"
fi

# Check if BOT_TOKEN is set
if grep -q "BOT_TOKEN=$" .env || grep -q "BOT_TOKEN=your-bot-token-from-botfather" .env; then
    echo ""
    echo "⚠️  IMPORTANT: You need to set your Telegram Bot Token!"
    echo "   1. Message @BotFather on Telegram"
    echo "   2. Create a new bot with /newbot"
    echo "   3. Copy the bot token"
    echo "   4. Edit the .env file and replace 'your-bot-token-from-botfather' with your actual token"
    echo ""
    read -p "Press Enter after you've updated the BOT_TOKEN in .env..."
fi

# Set up bot polling
echo "🤖 Setting up bot polling service..."

BOT_POLLING_DIR="../bot_polling"

if [ ! -d "$BOT_POLLING_DIR" ]; then
    echo "📥 Cloning bot polling repository..."
    git clone https://github.com/andrewvect/bot_polling.git "$BOT_POLLING_DIR"
else
    echo "✅ Bot polling repository already exists"
fi

# Build and run bot polling
echo "🔨 Building bot polling container..."
cd "$BOT_POLLING_DIR"
docker build -t bot_polling_image . || {
    echo "❌ Failed to build bot polling image"
    exit 1
}

# Stop existing container if running
if docker ps | grep -q bot_polling; then
    echo "🛑 Stopping existing bot polling container..."
    docker stop bot_polling
    docker rm bot_polling
fi

echo "🚀 Starting bot polling container..."
docker run -d --name bot_polling \
    -v "$(pwd)/../tg_bot/.env:/app/.env" \
    --network host \
    bot_polling_image || {
    echo "❌ Failed to start bot polling container"
    exit 1
}

cd - > /dev/null

echo "✅ Bot polling service started successfully!"

# Start the main application
echo "🚀 Starting the main application..."
docker compose build || {
    echo "❌ Failed to build application"
    exit 1
}

echo "🎉 Starting all services with docker compose watch..."
docker compose up --wait || {
    echo "❌ Failed to start services"
    exit 1
}

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "📱 Your bot is now running! Here's what to do next:"
echo "   1. Open Telegram and find your bot"
echo "   2. Send /start to begin"
echo "   3. Click 'Открыть приложение' to access the web interface"
echo ""
echo "🌐 Available services:"
echo "   • Backend API: http://localhost:8000"
echo "   • Frontend: http://localhost:5173"
echo "   • API Docs: http://localhost:8000/docs"
echo "   • Database Admin: http://localhost:8080"
echo ""
echo "🔧 To stop all services: docker compose down"
echo "📋 To view logs: docker compose logs -f"
echo ""
echo "Happy learning! 🇷🇸"