# Serbian Vocabulary Learning Telegram Bot

A modern vocabulary learning application that combines a Telegram bot with an embedded web application designed to help users efficiently learn new words and expand their vocabulary in Serbian language. The app utilizes a **spaced repetition algorithm (SRS)** to optimize the learning process and improve long-term retention of vocabulary.

## ✨ Features

- 🎯 **Spaced Repetition Learning**: Uses scientifically proven SRS algorithm for optimal memory retention
- 📚 **3700+ Serbian Words**: Vocabulary list based on frequency data from Wiktionary Serbian word list
- 🎨 **Interactive Web App**: Modern React-based interface embedded in Telegram
- 📊 **Progress Tracking**: Monitor your learning progress with detailed statistics
- ⚙️ **Customizable Settings**: Choose alphabet preferences (Cyrillic, Latin, or both)
- 🌍 **Multi-language Support**: Serbian words with translations and usage examples
- 🔄 **Adaptive Learning**: Algorithm adjusts based on your performance

## 📱 Screenshots

<p align="center">
    <img src="diagrams/1.jpeg" alt="Main Menu" width="20%" />
    <img src="diagrams/2.jpeg" alt="Learning Interface" width="20%" />
    <img src="diagrams/3.jpeg" alt="Word Examples" width="20%" />
    <img src="diagrams/4.jpeg" alt="Settings" width="20%" />
    <img src="diagrams/5.jpeg" alt="Adding Words" width="20%" />
</p>

## 🚀 Quick Start

### Option 1: Automated Setup (Recommended)

For the fastest setup, use our automated script:

```bash
git clone https://github.com/andrewvect/tg_bot.git
cd tg_bot
./scripts/quick-setup.sh
```

This script will:
- Check prerequisites
- Set up environment variables
- Clone and configure bot polling
- Build and start all services
- Guide you through bot token configuration

### Option 2: Manual Setup

### Prerequisites

Before you begin, ensure you have the following installed:
- **Docker** and **Docker Compose** (for easy setup)
- **Python 3.8+** and **Node.js 18+** (for local development)
- **Git** for cloning the repository

### 1. Clone the Repository

```bash
git clone https://github.com/andrewvect/tg_bot.git
cd tg_bot
```

### 2. Set Up Environment Variables

Create a `.env` file in the root directory based on the provided template:

```bash
cp .env.example .env  # if available, or create from template below
```

Essential variables to configure:

```env
# Telegram Bot Configuration
BOT_TOKEN=your_bot_token_here
TELEGRAM_TESTING=true  # Set to false for production

# Domain Configuration
DOMAIN=localhost.tiangolo.com  # For local development
ENVIRONMENT=local

# Database Configuration
POSTGRES_PASSWORD=your_secure_password
SECRET_KEY=your_secret_key_here

# Bot Content Source
URL_TO_GIT_FILES=https://raw.githubusercontent.com/andrewvect/words/refs/heads/main/
```

### 3. Get Your Bot Token

1. Message [@BotFather](https://t.me/BotFather) on Telegram
2. Create a new bot with `/newbot`
3. Copy the bot token and add it to your `.env` file
4. Set up bot commands (optional):
   ```
   start - Start learning vocabulary
   help - Get help and usage instructions
   ```

### 4. Set Up Bot Polling (Required)

The bot requires a separate polling service. Clone and set it up:

```bash
# In a separate directory
git clone https://github.com/andrewvect/bot_polling
cd bot_polling

# Build and run the polling container
docker build -t bot_polling_image .
docker run -d --name bot_polling \
    -v $(pwd)/../tg_bot/.env:/app/.env \
    bot_polling_image
```

### 5. Start the Application

```bash
# In the main tg_bot directory
docker compose watch
```

This will start:
- **Backend API**: http://localhost:8000
- **Frontend**: http://localhost:5173  
- **Database**: PostgreSQL on port 5432
- **Admin Panel**: http://localhost:8080 (Adminer)

### 6. Test Your Bot

1. Open Telegram and find your bot
2. Send `/start` to begin
3. Click "Открыть приложение" to access the web interface
4. Start learning vocabulary!

## 📖 How It Works

### Learning Process

1. **Word Discovery**: Choose whether you know a word when presented
2. **Spaced Repetition**: Words you're learning appear at calculated intervals
3. **Active Recall**: Try to remember the translation before revealing it
4. **Performance Tracking**: Mark if you remembered correctly or not
5. **Adaptive Scheduling**: Successfully recalled words appear less frequently

### Bot Commands

Once your bot is set up, users can interact with it using these commands:

- `/start` - Start learning vocabulary and see the main menu
- `/help` - Get detailed help and usage instructions

### Bot Features

**Main Menu Options:**
- 🔤 **Add New Words** - Learn new vocabulary from the 3700+ word database
- 🔄 **Review Words** - Practice words you've already started learning
- ⚙️ **Settings** - Customize your learning experience

**Learning Interface:**
- 👁️ **Spoiler Button** - Reveal translation and usage examples
- ✅ **Success Button** - Mark when you remembered correctly
- ❌ **Difficulty Button** - Mark when you had trouble remembering
- 📊 **Progress Tracking** - See how many words you've learned

**Customization Options:**
- **Alphabet Choice**: Learn with Cyrillic, Latin, or both scripts
- **Display Language**: Choose which language appears first
- **Random Mode**: Mix up word order for variety

### Language Levels

The vocabulary is organized by frequency and complexity:

- 🔸 **A1 — 500 words** (Basic phrases and daily communication)
- 🔸 **A2 — 1000 words** (Extended topics and travel)
- 🔸 **B1 — 2000 words** (Familiar topics, news comprehension)
- 🔸 **B2 — 3000 words** (Confident language use, dialogue)
- 🔸 **C1+ — 4000+ words** (Fluent speech, literature, complex topics)

## ⚙️ Configuration

### Environment Variables

Key configuration options in your `.env` file:

```env
# Bot Settings
BOT_TOKEN=              # Your Telegram bot token (required)
TELEGRAM_TESTING=true   # Use Telegram test environment
ADMIN_TG_ID=           # Your Telegram ID for admin features

# Application Settings
DOMAIN=localhost.tiangolo.com    # Your domain (use this for local dev)
ENVIRONMENT=local               # local, staging, or production
PROJECT_NAME="Serbian Vocabulary Bot"

# Security
SECRET_KEY=changethis          # Change to a secure random key
FIRST_SUPERUSER=admin@example.com
FIRST_SUPERUSER_PASSWORD=changethis8888

# Database
POSTGRES_PASSWORD=changethis   # Change to a secure password
POSTGRES_DB=app
POSTGRES_USER=postgres

# Content Source
URL_TO_GIT_FILES=https://raw.githubusercontent.com/andrewvect/words/refs/heads/main/
```

### Bot Customization

The bot's messages and content are configurable via `backend/content.yaml`. You can customize:
- Welcome messages
- Help text and instructions
- Feature descriptions
- Learning tips and motivation

## 🛠️ Development

For detailed development setup, see [development.md](./development.md).

### Local Development

```bash
# Backend development
cd backend
uv sync
source .venv/bin/activate
fastapi dev app/main.py

# Frontend development  
cd frontend
npm install
npm run dev
```

### Running Tests

```bash
# Backend tests
cd backend
bash ./scripts/test.sh

# Frontend tests
cd frontend
npx playwright test
```

## 🚀 Deployment

For production deployment instructions, see [deployment.md](./deployment.md).

The application supports deployment with:
- Docker Compose for simple deployments
- Traefik for reverse proxy and SSL
- GitHub Actions for CI/CD

## 🔧 Troubleshooting

### Common Issues

**Bot not responding:**
- Verify `BOT_TOKEN` is correctly set in `.env`
- Check if bot polling container is running: `docker ps | grep bot_polling`
- Ensure webhook is properly configured for production

**Database connection errors:**
- Verify PostgreSQL container is running: `docker compose ps`
- Check database credentials in `.env`
- Wait for database to be ready (first startup takes longer)

**Frontend not loading:**
- Check if all services are running: `docker compose ps`
- Verify `DOMAIN` configuration in `.env`
- Clear browser cache and try again

**Permission errors:**
- Ensure Docker has proper permissions
- Check file ownership: `sudo chown -R $USER:$USER .`

### Getting Help

- Check the logs: `docker compose logs [service_name]`
- Review [development.md](./development.md) for detailed setup
- Create an issue on GitHub for bugs or questions

## 📚 Documentation

- **[Technical Overview](./README_for_hiring_managers.md)** - Technology stack and architecture
- **[Development Guide](./development.md)** - Detailed development setup
- **[Deployment Guide](./deployment.md)** - Production deployment instructions
- **[Backend Documentation](./backend/README.md)** - Backend-specific information
- **[Frontend Documentation](./frontend/README.md)** - Frontend development guide

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make your changes and test thoroughly
4. Commit your changes: `git commit -m 'Add some feature'`
5. Push to the branch: `git push origin feature/your-feature`
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Ready to start learning Serbian vocabulary?** Follow the Quick Start guide above and begin your language learning journey! 🇷🇸
