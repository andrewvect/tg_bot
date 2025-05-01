# Full Stack FastAPI App

# WordGram - Language Learning Telegram Bot

A modern web application built with FastAPI backend and React frontend. This project combines a Telegram bot with an embedded web application designed to help users efficiently learn new words and expand their vocabulary. The system features user progress tracking, personalized learning paths, and intuitive word management, all accessible through the Telegram interface Web App.

## Technology Stack and Features

### Backend

- ⚡ [**FastAPI**](https://fastapi.tiangolo.com) for the Python backend API.
    - 🧰 [SQLAlchemy](https://www.sqlalchemy.org) for the Python SQL database interactions (ORM).
    - 🔍 [Pydantic](https://docs.pydantic.dev), used by FastAPI, for the data validation and settings management.
    - 💾 [PostgreSQL](https://www.postgresql.org) as the SQL database.
    - ✅ Tests with [Pytest](https://pytest.org).
    - 🔑 JWT (JSON Web Token) authentication.
    - 📨 [Aiogram](https://aiogram.dev) for Telegram bot development.

### Frontend

- 🚀 [React](https://react.dev) for the frontend.
    - 💃 Using TypeScript, hooks, Vite, and other parts of a modern frontend stack.
    - 🎨 [Chakra UI](https://chakra-ui.com) for the frontend components.
    - 🤖 An automatically generated frontend client.
    - 🧪 [Playwright](https://playwright.dev) for End-to-End testing.

### Infrastructure

- 🐋 [Docker Compose](https://www.docker.com) for development and production.
- 📞 [Traefik](https://traefik.io) as a reverse proxy / load balancer.
- 🚢 Deployment instructions using Docker Compose, including how to set up a frontend Traefik proxy to handle automatic HTTPS certificates.
- 📱 [Telegram API](https://core.telegram.org/bots/api) integration

## How To Use It or Run Locally



### Configure

You can then update configs in the `.env` files to customize your configurations.

## Backend Development

Backend docs: [backend/README.md](./backend/README.md).

## Frontend Development

Frontend docs: [frontend/README.md](./frontend/README.md).

## Deployment

Deployment docs: [deployment.md](./deployment.md).

## Development

General development docs: [development.md](./development.md).

This includes using Docker Compose, custom local domains, `.env` configurations, etc.

