# Project - Development

## Prerequisites

Before starting development, ensure you have:
- **Docker** and **Docker Compose** installed
- **Git** for version control
- **A Telegram Bot Token** (see setup instructions below)
- **Python 3.8+** and **Node.js 18+** (for local development without Docker)

## Initial Setup

### 1. Environment Configuration

Create a `.env` file in the root of the project, based on the `.env.example` file:

```bash
cp .env.example .env
```

**Important**: Edit the `.env` file and configure at least these essential variables:
- `BOT_TOKEN` - Your Telegram bot token (required)
- `POSTGRES_PASSWORD` - A secure password for the database
- `SECRET_KEY` - A secure random key for JWT tokens

### 2. Getting a Telegram Bot Token

1. Open Telegram and search for [@BotFather](https://t.me/BotFather)
2. Start a chat and use the `/newbot` command
3. Follow the prompts to create your bot:
   - Choose a name for your bot (e.g., "Serbian Vocab Bot")
   - Choose a username ending in "bot" (e.g., "serbian_vocab_bot")
4. Copy the bot token and add it to your `.env` file:
   ```env
   BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
   ```
5. (Optional) Configure bot commands with BotFather:
   ```
   start - Start learning vocabulary
   help - Get help and usage instructions
   ```

## Bot Polling Setup

**Important**: This bot requires a separate polling service to receive messages from Telegram.

### Why Bot Polling is Needed

The main application uses webhooks for production, but for development and some deployment scenarios, you need a polling service that:
- Continuously checks for new messages from Telegram
- Forwards them to your main application
- Handles the connection management

### Setting Up Bot Polling

1. **Clone the bot polling repository** (in a separate directory):
   ```bash
   # Navigate to your projects directory (not inside tg_bot)
   cd ../
   git clone https://github.com/andrewvect/bot_polling
   cd bot_polling
   ```

2. **Build the polling container**:
   ```bash
   docker build -t bot_polling_image .
   ```

3. **Run the polling container** with access to your `.env` file:
   ```bash
   docker run -d --name bot_polling \
       -v $(pwd)/../tg_bot/.env:/app/.env \
       --network host \
       bot_polling_image
   ```

4. **Verify it's running**:
   ```bash
   docker ps | grep bot_polling
   docker logs bot_polling
   ```

### Bot Polling Troubleshooting

If the bot doesn't respond to messages:
- Check if the polling container is running: `docker ps`
- Check the logs: `docker logs bot_polling`
- Verify your `BOT_TOKEN` is correct in the `.env` file
- Ensure the main application is accessible on `localhost:8000`

## Docker Compose

### Starting the Development Environment

Start the local stack with Docker Compose:

```bash
docker compose watch
```

This command will:
- Build and start all services (backend, frontend, database, etc.)
- Watch for changes and automatically rebuild/restart as needed
- Set up all necessary networks and volumes

### Accessing the Services

Once started, you can access:

- **Backend API**: http://localhost:8000
- **API Documentation (Swagger)**: http://localhost:8000/docs
- **Alternative API Docs (ReDoc)**: http://localhost:8000/redoc
- **Frontend Web App**: http://localhost:5173
- **Database Admin (Adminer)**: http://localhost:8080
- **Traefik Dashboard**: http://localhost:8090
- **MailCatcher** (if configured): http://localhost:1080

### First Startup

**Note**: The first time you start your stack, it might take a few minutes to be ready while:
- Docker downloads and builds images
- The database initializes
- The backend waits for the database and configures everything
- Dependencies are installed

### Monitoring the Startup

To check the logs and monitor the startup process:

```bash
# View logs from all services
docker compose logs

# Follow logs in real-time
docker compose logs -f

# Check logs for a specific service
docker compose logs backend
docker compose logs frontend
docker compose logs db
```

### Testing Your Bot

1. **Start the bot polling service** (see Bot Polling Setup above)
2. **Open Telegram** and find your bot
3. **Send `/start`** to your bot
4. **Click "Открыть приложение"** to open the web interface
5. **Start learning!** Try adding words and testing the spaced repetition system

## Troubleshooting

### Common Development Issues

#### Bot Not Responding

**Problem**: Bot doesn't respond to Telegram messages

**Solutions**:
1. **Check bot polling service**:
   ```bash
   docker ps | grep bot_polling  # Should show running container
   docker logs bot_polling       # Check for errors
   ```

2. **Verify bot token**:
   ```bash
   grep BOT_TOKEN .env  # Ensure it's set correctly
   ```

3. **Check main application**:
   ```bash
   curl http://localhost:8000/health  # Should return OK
   docker compose logs backend        # Check backend logs
   ```

4. **Restart services**:
   ```bash
   docker restart bot_polling
   docker compose restart backend
   ```

#### Database Connection Issues

**Problem**: Database connection errors or migrations failing

**Solutions**:
1. **Check database status**:
   ```bash
   docker compose ps db           # Should show healthy
   docker compose logs db         # Check database logs
   ```

2. **Wait for database initialization**:
   ```bash
   # Database needs time to initialize on first run
   docker compose logs db | grep "ready to accept connections"
   ```

3. **Reset database** (if needed):
   ```bash
   docker compose down -v  # Warning: This deletes all data
   docker compose up -d db
   ```

#### Frontend Not Loading

**Problem**: Frontend shows blank page or errors

**Solutions**:
1. **Check frontend service**:
   ```bash
   docker compose logs frontend
   curl http://localhost:5173
   ```

2. **Verify environment variables**:
   ```bash
   grep DOMAIN .env
   grep FRONTEND_HOST .env
   ```

3. **Clear browser cache** and try again

4. **Rebuild frontend**:
   ```bash
   docker compose build frontend
   docker compose up -d frontend
   ```

#### Permission Errors

**Problem**: Permission denied errors with Docker or file access

**Solutions**:
1. **Fix file ownership**:
   ```bash
   sudo chown -R $USER:$USER .
   ```

2. **Add user to docker group**:
   ```bash
   sudo usermod -aG docker $USER
   # Log out and log back in
   ```

#### Port Already in Use

**Problem**: "Port already in use" errors

**Solutions**:
1. **Check what's using the port**:
   ```bash
   sudo lsof -i :8000  # Check port 8000
   sudo lsof -i :5173  # Check port 5173
   ```

2. **Stop conflicting services**:
   ```bash
   docker compose down
   # Kill specific processes if needed
   ```

3. **Change ports in docker-compose.override.yml** if needed

### Development Tips

#### Viewing Logs Effectively

```bash
# Follow logs from all services with timestamps
docker compose logs -f -t

# Filter logs for specific patterns
docker compose logs backend | grep ERROR
docker compose logs | grep -i webhook

# View logs for the last 10 minutes
docker compose logs --since 10m
```

#### Database Management

```bash
# Access database directly
docker compose exec db psql -U postgres -d app

# Run database migrations
docker compose exec backend alembic upgrade head

# Create new migration
docker compose exec backend alembic revision --autogenerate -m "description"
```

#### Working with Bot Content

```bash
# Edit bot messages
nano backend/content.yaml

# The content is automatically reloaded when the backend restarts
docker compose restart backend
```

### Getting Help

If you're still having issues:

1. **Check the logs** for specific error messages
2. **Search the repository issues** on GitHub
3. **Create a new issue** with:
   - Your operating system
   - Docker and Docker Compose versions
   - Complete error messages
   - Steps to reproduce the problem

## Contributing to Development

### Making Changes

1. **Fork the repository** and create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following the project conventions:
   - Backend: Follow FastAPI and SQLAlchemy best practices
   - Frontend: Use TypeScript and follow React patterns
   - Bot: Update content.yaml for message changes

3. **Test your changes**:
   ```bash
   # Backend tests
   docker compose exec backend bash scripts/tests-start.sh
   
   # Frontend tests
   cd frontend && npx playwright test
   
   # Manual testing with your bot
   ```

4. **Commit and push**:
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   git push origin feature/your-feature-name
   ```

5. **Create a Pull Request** with a clear description of your changes

### Code Style

- **Python**: Code is automatically formatted with `ruff`
- **TypeScript/React**: Code is formatted with `prettier` and linted with `eslint`
- **Commits**: Use conventional commit messages (feat:, fix:, docs:, etc.)
- **Pre-commit hooks**: Install with `uv run pre-commit install`

### Development Guidelines

- **Keep it simple**: Make minimal changes that solve specific problems
- **Test thoroughly**: Ensure your changes don't break existing functionality
- **Document changes**: Update relevant documentation files
- **Follow patterns**: Maintain consistency with existing code structure

## Local Development

The Docker Compose files are configured so that each of the services is available in a different port in `localhost`.

For the backend and frontend, they use the same port that would be used by their local development server, so, the backend is at `http://localhost:8000` and the frontend at `http://localhost:5173`.

This way, you could turn off a Docker Compose service and start its local development service, and everything would keep working, because it all uses the same ports.

For example, you can stop that `frontend` service in the Docker Compose, in another terminal, run:

```bash
docker compose stop frontend
```

And then start the local frontend development server:

```bash
cd frontend
npm run dev
```

Or you could stop the `backend` Docker Compose service:

```bash
docker compose stop backend
```

And then you can run the local development server for the backend:

```bash
cd backend
fastapi dev app/main.py
```

## Docker Compose in `localhost.tiangolo.com`

When you start the Docker Compose stack, it uses `localhost` by default, with different ports for each service (backend, frontend, adminer, etc).

When you deploy it to production (or staging), it will deploy each service in a different subdomain, like `api.example.com` for the backend and `dashboard.example.com` for the frontend.

In the guide about [deployment](deployment.md) you can read about Traefik, the configured proxy. That's the component in charge of transmitting traffic to each service based on the subdomain.

If you want to test that it's all working locally, you can edit the local `.env` file, and change:

```dotenv
DOMAIN=localhost.tiangolo.com
```

That will be used by the Docker Compose files to configure the base domain for the services.

Traefik will use this to transmit traffic at `api.localhost.tiangolo.com` to the backend, and traffic at `dashboard.localhost.tiangolo.com` to the frontend.

The domain `localhost.tiangolo.com` is a special domain that is configured (with all its subdomains) to point to `127.0.0.1`. This way you can use that for your local development.

After you update it, run again:

```bash
docker compose watch
```

When deploying, for example in production, the main Traefik is configured outside of the Docker Compose files. For local development, there's an included Traefik in `docker-compose.override.yml`, just to let you test that the domains work as expected, for example with `api.localhost.tiangolo.com` and `dashboard.localhost.tiangolo.com`.

## Docker Compose files and env vars

There is a main `docker-compose.yml` file with all the configurations that apply to the whole stack, it is used automatically by `docker compose`.

And there's also a `docker-compose.override.yml` with overrides for development, for example to mount the source code as a volume. It is used automatically by `docker compose` to apply overrides on top of `docker-compose.yml`.

These Docker Compose files use the `.env` file containing configurations to be injected as environment variables in the containers.

They also use some additional configurations taken from environment variables set in the scripts before calling the `docker compose` command.

After changing variables, make sure you restart the stack:

```bash
docker compose watch
```

## The .env file

The `.env` file is the one that contains all your configurations, generated keys and passwords, etc.

Depending on your workflow, you could want to exclude it from Git, for example if your project is public. In that case, you would have to make sure to set up a way for your CI tools to obtain it while building or deploying your project.

One way to do it could be to add each environment variable to your CI/CD system, and updating the `docker-compose.yml` file to read that specific env var instead of reading the `.env` file.

## Pre-commits and code linting

we are using a tool called [pre-commit](https://pre-commit.com/) for code linting and formatting.

When you install it, it runs right before making a commit in git. This way it ensures that the code is consistent and formatted even before it is committed.

You can find a file `.pre-commit-config.yaml` with configurations at the root of the project.

#### Install pre-commit to run automatically

`pre-commit` is already part of the dependencies of the project, but you could also install it globally if you prefer to, following [the official pre-commit docs](https://pre-commit.com/).

After having the `pre-commit` tool installed and available, you need to "install" it in the local repository, so that it runs automatically before each commit.

Using `uv`, you could do it with:

```bash
❯ uv run pre-commit install
pre-commit installed at .git/hooks/pre-commit
```

Now whenever you try to commit, e.g. with:

```bash
git commit
```

...pre-commit will run and check and format the code you are about to commit, and will ask you to add that code (stage it) with git again before committing.

Then you can `git add` the modified/fixed files again and now you can commit.

#### Running pre-commit hooks manually

you can also run `pre-commit` manually on all the files, you can do it using `uv` with:

```bash
❯ uv run pre-commit run --all-files
check for added large files..............................................Passed
check toml...............................................................Passed
check yaml...............................................................Passed
ruff.....................................................................Passed
ruff-format..............................................................Passed
eslint...................................................................Passed
prettier.................................................................Passed
```

## URLs

The production or staging URLs would use these same paths, but with your own domain.

### Development URLs

Development URLs, for local development.

Frontend: http://localhost:5173

Backend: http://localhost:8000

Automatic Interactive Docs (Swagger UI): http://localhost:8000/docs

Automatic Alternative Docs (ReDoc): http://localhost:8000/redoc

Adminer: http://localhost:8080

Traefik UI: http://localhost:8090

MailCatcher: http://localhost:1080

### Development URLs with `localhost.tiangolo.com` Configured

Development URLs, for local development.

Frontend: http://dashboard.localhost.tiangolo.com

Backend: http://api.localhost.tiangolo.com

Automatic Interactive Docs (Swagger UI): http://api.localhost.tiangolo.com/docs

Automatic Alternative Docs (ReDoc): http://api.localhost.tiangolo.com/redoc

Adminer: http://localhost.tiangolo.com:8080

Traefik UI: http://localhost.tiangolo.com:8090

MailCatcher: http://localhost.tiangolo.com:1080
