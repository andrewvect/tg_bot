
# Serbian Vocabulary Learning Bot - Technical Overview

This document provides a comprehensive technical overview of the Serbian vocabulary learning bot, including architecture, technology choices, and implementation details.

## Technology Stack and Features

This vocabulary learning bot demonstrates modern full-stack development practices with a focus on educational technology and user experience optimization.

### Backend

- ⚡ [**FastAPI**](https://fastapi.tiangolo.com) for the Python backend API
    - 🧰 [SQLAlchemy](https://www.sqlalchemy.org) for the Python SQL database interactions (ORM)
    - 🔍 [Pydantic](https://docs.pydantic.dev), used by FastAPI, for data validation and settings management
    - 💾 [PostgreSQL](https://www.postgresql.org) as the SQL database
    - ✅ Tests with [Pytest](https://pytest.org)
    - 🔑 JWT (JSON Web Token) authentication
    - 📨 [Aiogram](https://aiogram.dev) for Telegram bot development
    - 🔄 **Spaced Repetition Algorithm** implementation for optimal learning
    - 📊 **Learning Analytics** tracking user progress and performance

### Frontend

- 🚀 [React](https://react.dev) for the frontend
    - 💃 Using TypeScript, hooks, Vite, and other parts of a modern frontend stack
    - 🎨 [Chakra UI](https://chakra-ui.com) for the frontend components
    - 🤖 An automatically generated frontend client
    - 🧪 [Playwright](https://playwright.dev) for End-to-End testing
    - 📱 **Telegram Web App** integration for seamless bot experience
    - 🎯 **Interactive Learning Interface** optimized for vocabulary acquisition

### Telegram Bot Features

- 🤖 **Native Telegram Integration** with webhook and polling support
- 🌐 **Embedded Web Application** using Telegram's Web App API
- 📚 **Vocabulary Management System** with 3700+ Serbian words
- 🧠 **Adaptive Learning Algorithm** based on spaced repetition principles
- ⚙️ **User Customization** (alphabet preferences, learning settings)
- 📈 **Progress Tracking** with detailed statistics and analytics
- 🔄 **Content Management** via YAML configuration files
- 🎌 **Multi-language Support** (Serbian Cyrillic/Latin, with translations)

### Infrastructure

- 🐋 [Docker Compose](https://www.docker.com) for development and production
- 📞 [Traefik](https://traefik.io) as a reverse proxy / load balancer
- 🚢 Deployment instructions using Docker Compose, including how to set up a frontend Traefik proxy to handle automatic HTTPS certificates
- 📱 [Telegram API](https://core.telegram.org/bots/api) integration
- 🔧 **Bot Polling Service** for development and webhook alternatives
- 📊 **Database Migrations** with Alembic
- 🧪 **Comprehensive Testing** (unit, integration, E2E)

Services architecture visualization:
![Architecture](diagrams/architecture.svg)

## Educational Algorithm Implementation

### Spaced Repetition System (SRS)

The bot implements a sophisticated spaced repetition algorithm optimized for vocabulary acquisition:

**Algorithm Components:**
- **Initial Presentation**: New words are presented for familiarity assessment
- **Interval Calculation**: Based on performance, intervals between reviews are calculated
- **Difficulty Adjustment**: Words that are harder to remember get shorter intervals
- **Mastery Tracking**: Successfully recalled words graduate to longer intervals
- **Review Scheduling**: Smart scheduling ensures optimal memory retention

**Performance Metrics:**
- User response accuracy tracking
- Learning curve analysis
- Retention rate optimization
- Adaptive difficulty scaling

### Database Schema Design

The application uses a normalized database schema designed for educational efficiency:

```sql
-- Core learning entities
Users: Telegram ID, settings, progress tracking
Words: Serbian vocabulary with frequency rankings
UserWords: Individual learning progress per word
Settings: Customizable learning preferences
WordExamples: Usage examples in both languages
```

**Key Features:**
- Optimized for fast word retrieval during learning sessions
- Efficient progress tracking with minimal storage overhead
- Scalable design supporting thousands of users
- Historical data preservation for learning analytics

## Bot Architecture Patterns

### Webhook vs Polling Architecture

**Production (Webhook Mode):**
```
Telegram → Webhook → FastAPI Backend → Database
                  ↓
              Web App Integration
```

**Development (Polling Mode):**
```
Telegram ← Bot Polling Service ← FastAPI Backend ← Database
                              ↓
                         Web App Integration
```

### Microservices Design

- **Backend API**: Core business logic and data management
- **Bot Polling Service**: Telegram message handling (development)
- **Frontend Web App**: Interactive learning interface
- **Database**: Persistent data storage
- **Content Management**: YAML-based configuration

## Quick Start Guide

### Prerequisites

Before running the application, ensure you have the following installed:
- **Python 3.8+** for backend development
- **Node.js 18+** and npm for frontend development
- **Docker** and **Docker Compose** for containerized deployment
- **Git** for version control
- **A Telegram Bot Token** from [@BotFather](https://t.me/BotFather)

### Step-by-Step Setup

1. **Clone and Configure**:
   ```bash
   git clone https://github.com/andrewvect/tg_bot.git
   cd tg_bot
   cp .env.example .env
   # Edit .env with your bot token and configuration
   ```

2. **Set Up Bot Polling** (required for development):
   ```bash
   git clone https://github.com/andrewvect/bot_polling ../bot_polling
   cd ../bot_polling
   docker build -t bot_polling_image .
   docker run -d --name bot_polling \
       -v $(pwd)/../tg_bot/.env:/app/.env \
       --network host bot_polling_image
   ```

3. **Start the Application**:
   ```bash
   cd ../tg_bot
   docker compose watch
   ```

4. **Test the Bot**:
   - Message your bot on Telegram with `/start`
   - Click "Открыть приложение" to access the web interface
   - Begin learning Serbian vocabulary!

### Development Workflow

The application supports hot-reload development:
- **Backend changes**: Automatically reload with FastAPI
- **Frontend changes**: Hot module replacement with Vite
- **Database changes**: Managed with Alembic migrations
- **Bot content**: YAML configuration with restart

### Configuration Options

Key environment variables for customization:

```env
# Core Bot Configuration
BOT_TOKEN=your_telegram_bot_token
TELEGRAM_TESTING=true  # Use test environment
ADMIN_TG_ID=your_telegram_id

# Learning Content
URL_TO_GIT_FILES=https://github.com/andrewvect/words/raw/main/
# Points to Serbian vocabulary data repository

# Application Settings  
DOMAIN=localhost.tiangolo.com  # Local development domain
ENVIRONMENT=local              # Environment type
```

## Backend Development

Backend docs: [backend/README.md](./backend/README.md).

## Frontend Development

Frontend docs: [frontend/README.md](./frontend/README.md).

## Deployment

Deployment docs: [deployment.md](./deployment.md).

## Development

General development docs: [development.md](./development.md).

This includes using Docker Compose, custom local domains, `.env` configurations, etc.
