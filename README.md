# 🏥 Citizen Affiliation Microservice

A Django-based microservice for checking citizen affiliation eligibility and authenticating documents. Built with cloud-native best practices, event-driven architecture, and complete CI/CD pipeline.

## 📋 Table of Contents

- [Features](#features)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Development](#development)
- [Docker Setup](#docker-setup)
- [API Documentation](#api-documentation)
- [Testing](#testing)
- [Monitoring](#monitoring)
- [Documentation](#documentation)

## ✨ Features

### Core Functionality
- ✅ **Citizen Affiliation Checker**: Validate eligibility through external API integration
- ✅ **Document Authentication**: Authenticate and validate citizen documents
- ✅ **Event-Driven Architecture**: RabbitMQ for asynchronous event publishing
- ✅ **JWT Authentication**: Secure API endpoints with JSON Web Tokens

### Technical Features
- ✅ **RESTful API**: Built with Django REST Framework
- ✅ **Database**: MariaDB/MySQL for data persistence
- ✅ **Cache**: Redis for JWT blacklist and performance
- ✅ **Message Queue**: RabbitMQ for event publishing
- ✅ **Monitoring**: Prometheus + Grafana
- ✅ **API Documentation**: Auto-generated with drf-spectacular (OpenAPI/Swagger)
- ✅ **Health Checks**: Liveness and readiness endpoints
- ✅ **Containerized**: Docker and Docker Compose ready
- ✅ **Cloud-Native**: Environment-based configuration

## 🛠️ Technology Stack

### Backend
- **Framework**: Django 5.0.6 + Django REST Framework 3.15.1
- **Language**: Python 3.12
- **Database**: MariaDB 10.11 (MySQL compatible)
- **Cache**: Redis 7
- **Message Broker**: RabbitMQ 3 with Management UI

### DevOps & Infrastructure
- **Containerization**: Docker + Docker Compose
- **Monitoring**: Prometheus + Grafana
- **API Docs**: drf-spectacular (OpenAPI 3.0)
- **Auth**: JWT (djangorestframework-simplejwt)

### Development Tools
- **Testing**: pytest, pytest-django, pytest-cov
- **Code Quality**: black, flake8, isort, pylint
- **Security**: bandit

## 📁 Project Structure

```
project_connectivity/
├── apps/                          # Django applications
│   ├── affiliation/              # Affiliation checking logic
│   ├── authentication/           # JWT authentication
│   ├── documents/                # Document authentication
│   └── core/                     # Shared utilities
├── infrastructure/               # External integrations
│   ├── rabbitmq/                # RabbitMQ event publishing
│   └── external_apis/           # External API clients
├── settings/                     # Django settings
│   ├── settings.py              # Main configuration
│   ├── urls.py                  # URL routing
│   └── wsgi.py                  # WSGI application
├── monitoring/                   # Monitoring configuration
│   ├── prometheus/              # Prometheus config
│   └── grafana/                 # Grafana dashboards
├── requirements/                 # Python dependencies
│   ├── base.txt                 # Production dependencies
│   └── dev.txt                  # Development dependencies
├── logs/                         # Application logs
├── docker-compose.yml            # Docker services definition
├── Dockerfile                    # Production Docker image
├── pytest.ini                    # pytest configuration
├── setup.cfg                     # Tool configurations
├── .env.example                  # Environment variables template
└── manage.py                     # Django management script
```

## 🚀 Getting Started

### Prerequisites

- Python 3.12+
- Docker and Docker Compose (for containerized setup)
- MariaDB/MySQL 10.11+ (for local development without Docker)
- Redis 7+ (for local development without Docker)
- RabbitMQ 3+ (for local development without Docker)

### Local Development Setup

1. **Clone the repository**
   ```bash
   cd /home/alejo/connectivity/project_connectivity
   ```

2. **Create and activate virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Linux/Mac
   # or
   venv\\Scripts\\activate  # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements/dev.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run development server**
   ```bash
   python manage.py runserver
   ```

   The API will be available at `http://localhost:8000`

## 🐳 Docker Setup

### Quick Start with Docker Compose

1. **Start all services**
   ```bash
   docker-compose up -d
   ```

   This will start:
   - **MariaDB** (port 3306)
   - **Redis** (port 6379)
   - **RabbitMQ** (AMQP: 5672, Management UI: 15672)
   - **Django App** (port 8000)
   - **Prometheus** (port 9090)
   - **Grafana** (port 3000)

2. **View logs**
   ```bash
   docker-compose logs -f web
   ```

3. **Run migrations**
   ```bash
   docker-compose exec web python manage.py migrate
   ```

4. **Create superuser**
   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

5. **Stop services**
   ```bash
   docker-compose down
   ```

### Access Points

- **Django API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/api/schema/swagger-ui/
- **Admin Panel**: http://localhost:8000/admin/
- **RabbitMQ Management**: http://localhost:15672 (admin/admin)
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000 (admin/admin)

## 📚 API Documentation

### Endpoints

#### Authentication
- `POST /api/v1/auth/login/` - Login and get JWT tokens
- `POST /api/v1/auth/refresh/` - Refresh access token
- `POST /api/v1/auth/logout/` - Logout (blacklist token)

#### Affiliation
- `POST /api/v1/affiliation/check/` - Check citizen affiliation eligibility

#### Documents
- `POST /api/v1/documents/authenticate/` - Authenticate citizen documents

#### Health & Monitoring
- `GET /health/live/` - Liveness probe
- `GET /health/ready/` - Readiness probe
- `GET /metrics/` - Prometheus metrics

### Interactive API Documentation

Visit http://localhost:8000/api/schema/swagger-ui/ for interactive API documentation with Swagger UI.

## 🧪 Testing

### Run all tests
```bash
pytest
```

### Run with coverage
```bash
pytest --cov=apps --cov=infrastructure --cov-report=html
```

### Run specific test types
```bash
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only
pytest -m e2e           # End-to-end tests only
```

### View coverage report
```bash
open htmlcov/index.html  # or your browser
```

## 📊 Monitoring

### Prometheus

Access Prometheus at http://localhost:9090

Key metrics available:
- Request rate
- Response time
- Error rate
- Database queries
- RabbitMQ queue depth

### Grafana

Access Grafana at http://localhost:3000 (admin/admin)

Pre-configured dashboards for:
- Django application metrics
- Database performance
- RabbitMQ metrics
- System resources

## 🔧 Development

### Code Quality

```bash
# Format code with black
black apps/ infrastructure/

# Sort imports
isort apps/ infrastructure/

# Lint with flake8
flake8 apps/ infrastructure/

# Type checking with pylint
pylint apps/ infrastructure/

# Security check
bandit -r apps/ infrastructure/
```

### Database Migrations

```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Show migrations
python manage.py showmigrations
```

## 🌍 Environment Variables

See `.env.example` for all available configuration options.

### Key Variables

```bash
# Core
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=mysql://user:password@host:3306/database

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# RabbitMQ
RABBITMQ_HOST=localhost
RABBITMQ_PORT=5672
RABBITMQ_USER=guest
RABBITMQ_PASSWORD=guest

# JWT
JWT_SECRET_KEY=your-jwt-secret
JWT_ACCESS_TOKEN_MINUTES=15
JWT_REFRESH_TOKEN_DAYS=7

# External API
EXTERNAL_AFFILIATION_API_URL=https://api.example.com
EXTERNAL_AFFILIATION_API_KEY=your-api-key
```

## 📖 Documentation

All documentation is organized in the `/docs` folder:

- **[📚 Documentation Index](docs/INDEX.md)** - Complete documentation index

### Quick Links
- **Getting Started**: [Quick Start Guide](docs/QUICK_START.md)
- **Development**: [Affiliation Implementation](docs/AFFILIATION_IMPLEMENTATION_SUMMARY.md)
- **Deployment**: [CI/CD Deployment Guide](docs/CICD_DEPLOYMENT_GUIDE.md)
- **Operations**: [CI/CD Quick Reference](docs/CICD_QUICK_REFERENCE.md)
- **Kubernetes**: [K8s Local Testing](docs/K8S_LOCAL_TESTING.md)
- **Security**: [Production User Management](docs/PRODUCTION_USER_MANAGEMENT.md)
- **Integration**: [Service-to-Service Auth](docs/SERVICE_TO_SERVICE_AUTH.md)
- **Status**: [Project Status](docs/PROJECT_STATUS.md)

Visit the [Documentation Index](docs/INDEX.md) for a complete list organized by role and category.

## 🤝 Contributing

1. Create a feature branch
2. Make your changes
3. Run tests and linting
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 👥 Authors

- Development Team

## 🔗 Related Projects

- **Reference Project**: [citizen-affiliation-service](/home/alejo/citizen-affiliation-service)
- **Auth Microservice**: [auth-microservice](/home/alejo/Kris/auth-microservice)
