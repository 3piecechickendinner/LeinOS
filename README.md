# LienOS

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Status](https://img.shields.io/badge/Status-Production%20Ready-green.svg)

**AI-Powered Tax Lien Portfolio Management System**

LienOS is an intelligent multi-agent system that automates tax lien investment operations. Unlike passive tracking tools, LienOS employs proactive AI agents that monitor deadlines, calculate interest, process payments, and generate documents—all without manual intervention.

## Why LienOS?

Tax lien investing is profitable but operationally complex. Investors must track redemption deadlines, calculate accruing interest, manage payments, and generate legal documents across potentially hundreds of liens. Missing a single deadline can mean losing an investment.

**LienOS solves this with AI agents that:**
- Proactively alert you before deadlines (90, 60, 30, 14, 7, 3, 1 days)
- Automatically calculate interest using state-specific rules
- Track payments and detect full redemption
- Generate professional documents on demand
- Provide portfolio analytics and recommendations

**Built for:** Tax lien investors, real estate course graduates, and investment firms managing lien portfolios.

---

## Architecture

LienOS uses a **multi-agent architecture** powered by Google's Agent Development Kit (ADK) and Gemini AI models.

### The 7-Agent System

| Agent | Responsibility |
|-------|----------------|
| **LienTrackerAgent** | CRUD operations for lien records |
| **InterestCalculatorAgent** | Calculate accrued interest and total owed |
| **DeadlineAlertAgent** | Monitor deadlines and send proactive alerts |
| **PaymentMonitorAgent** | Record payments, detect redemption |
| **CommunicationAgent** | Manage notifications, email/SMS queues |
| **PortfolioDashboardAgent** | Analytics, performance metrics, recommendations |
| **DocumentGeneratorAgent** | Generate notices, receipts, reports, tax forms |

### Root Orchestrator Agent

The `root_agent` in `agents/agent.py` orchestrates all 7 specialized agents, providing a unified conversational interface powered by Gemini 2.0 Flash. Users can interact naturally with the system, and the orchestrator routes requests to the appropriate specialized agent.

### Tech Stack

- **AI Framework:** Google ADK + Gemini 2.0 Flash
- **Backend:** FastAPI (async Python)
- **Database:** Google Firestore (with local dev mode)
- **Validation:** Pydantic v2
- **Testing:** Pytest + pytest-asyncio
- **Deployment:** Cloud Run, Docker, Terraform
- **CI/CD:** Google Cloud Build
- **Observability:** OpenTelemetry, Cloud Trace, Cloud Logging

### Design Principles

- **Multi-tenant:** Complete data isolation per tenant
- **Agent-first:** Business logic lives in specialized agents
- **Async throughout:** Non-blocking operations for scale
- **Local-first development:** Works without cloud credentials
- **Production-ready:** Containerized, observable, auto-scaling

---

## Quick Start

### Prerequisites

- **Python 3.11+**
- **uv**: Python package manager - [Install](https://docs.astral.sh/uv/getting-started/installation/)
- **Google Cloud SDK** (for deployment): [Install](https://cloud.google.com/sdk/docs/install)
- **make**: Build automation tool (pre-installed on Unix systems)

### Installation

```bash
# Clone the repository
git clone https://github.com/3piecechickendinner/LienOS.git
cd lien-os

# Install dependencies
make install
```

### Local Development

#### Option 1: Run ADK Playground (Recommended for Testing)

```bash
# Launch interactive playground with UI
make playground
```

This starts the ADK web interface where you can chat with the LienOS orchestrator agent and test all capabilities.

#### Option 2: Run REST API

```bash
# Start the FastAPI development server
make local-backend
```

The API will be available at `http://localhost:8000`

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

### Run Tests

```bash
# Run all tests
make test

# Run code quality checks
make lint
```

---

## API Documentation

Interactive API documentation is available when the server is running at http://localhost:8000/docs

### Example API Calls

**Create a Lien:**
```bash
curl -X POST http://localhost:8000/api/liens \
  -H "Content-Type: application/json" \
  -H "X-Tenant-ID: my-tenant-id" \
  -d '{
    "certificate_number": "2024-001",
    "purchase_amount": 5000,
    "interest_rate": 18,
    "sale_date": "2024-01-15",
    "redemption_deadline": "2026-01-15",
    "county": "Miami-Dade",
    "property_address": "123 Main St, Miami, FL 33101",
    "parcel_id": "12-34-56-789"
  }'
```

**Calculate Interest:**
```bash
curl -X POST http://localhost:8000/api/interest/calculate \
  -H "Content-Type: application/json" \
  -H "X-Tenant-ID: my-tenant-id" \
  -d '{"lien_id": "lien_2024-001_20240115120000"}'
```

**Get Portfolio Summary:**
```bash
curl -X POST http://localhost:8000/api/portfolio/summary \
  -H "X-Tenant-ID: my-tenant-id"
```

**Generate Redemption Notice:**
```bash
curl -X POST http://localhost:8000/api/documents/redemption-notice \
  -H "Content-Type: application/json" \
  -H "X-Tenant-ID: my-tenant-id" \
  -d '{"lien_id": "lien_2024-001_20240115120000"}'
```

---

## Production Deployment

LienOS is production-ready with automated deployment to Google Cloud Run.

### Deployment Commands

| Command | Description |
|---------|-------------|
| `make install` | Install dependencies using uv |
| `make playground` | Launch ADK playground for agent testing |
| `make local-backend` | Run FastAPI server locally |
| `make deploy` | Deploy to Cloud Run (dev environment) |
| `make test` | Run unit and integration tests |
| `make lint` | Run code quality checks |
| `make setup-dev-env` | Set up infrastructure with Terraform |

### Deploy to Cloud Run

#### Quick Deploy (Dev Environment)

```bash
# Set your Google Cloud project
gcloud config set project YOUR-PROJECT-ID

# Deploy directly to Cloud Run
make deploy
```

This will:
1. Build a Docker container
2. Push to Google Artifact Registry
3. Deploy to Cloud Run in us-central1
4. Enable authentication (--no-allow-unauthenticated)
5. Allocate 4GB memory with no CPU throttling

#### Advanced Deploy Options

```bash
# Deploy with Identity-Aware Proxy (IAP)
make deploy IAP=true

# Deploy with custom port
make deploy PORT=8080
```

### CI/CD Pipeline

LienOS includes Google Cloud Build pipelines for automated deployment:

#### Staging Pipeline (`.cloudbuild/staging.yaml`)
- Triggered on pull requests or pushes to `staging` branch
- Builds and deploys to staging environment
- Runs load tests with Locust
- Auto-triggers production deployment on success

#### Production Pipeline (`.cloudbuild/deploy-to-prod.yaml`)
- Triggered manually or by staging pipeline
- Deploys to production with approval gates
- Includes rollback capabilities

#### PR Checks (`.cloudbuild/pr_checks.yaml`)
- Runs on all pull requests
- Executes linting, testing, and security checks
- Blocks merge if checks fail

### Set Up CI/CD

For a streamlined one-command setup:

```bash
uvx agent-starter-pack setup-cicd
```

This automates:
- Cloud Build trigger creation
- IAM permission setup
- Artifact Registry configuration
- Environment variable configuration

### Infrastructure as Code

Infrastructure is managed with Terraform in `deployment/terraform/`:

```bash
# Initialize and deploy development infrastructure
make setup-dev-env
```

This creates:
- Cloud Run service
- Artifact Registry repository
- GCS buckets for logs and artifacts
- IAM roles and permissions
- Firestore database
- Cloud Logging configuration

See [deployment/README.md](deployment/README.md) for detailed Terraform documentation.

---

## Configuration

### Environment Variables

Create a `.env` file based on `.env.example`:

```bash
cp .env.example .env
```

**Required for Production:**
```bash
GOOGLE_PROJECT_ID=your-project-id
GOOGLE_CLOUD_LOCATION=us-central1
LOGS_BUCKET_NAME=your-logs-bucket
```

**Optional:**
```bash
# Telemetry
OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT=NO_CONTENT

# CORS (for frontend)
ALLOW_ORIGINS=https://yourfrontend.com,https://app.yourfrontend.com

# Commit tracking
COMMIT_SHA=<auto-set-by-ci-cd>
AGENT_VERSION=<auto-set-by-ci-cd>
```

### Local Development (No Cloud Required)

LienOS works fully offline for development:

```bash
# Set local mode
export GOOGLE_PROJECT_ID=local-dev

# Run locally
make local-backend
```

In local mode:
- Firestore uses in-memory mock storage
- No Google Cloud credentials needed
- Perfect for testing and development

---

## Monitoring and Observability

LienOS includes production-grade observability:

### 1. Agent Telemetry (Always Enabled)
- **OpenTelemetry traces** exported to Cloud Trace
- Tracks agent execution, latency, and system metrics
- No PII or prompt content logged

### 2. Prompt-Response Logging (Production Only)
- Metadata-only logging to GCS and BigQuery
- Enabled when `LOGS_BUCKET_NAME` is set
- Helps with debugging and performance analysis
- **Local development:** Disabled by default

### View Telemetry

```bash
# Cloud Trace
https://console.cloud.google.com/traces

# Cloud Logging
https://console.cloud.google.com/logs

# GCS telemetry data
gs://YOUR-LOGS-BUCKET/completions/
```

---

## Project Structure

```
lien-os/
├── agents/                     # AI agents and orchestrator
│   ├── agent.py               # Root orchestrator agent
│   ├── interest_calculator/   # Interest calculation agent
│   ├── deadline_alert/        # Deadline monitoring agent
│   ├── payment_monitor/       # Payment tracking agent
│   ├── lien_tracker/          # Lien CRUD agent
│   ├── communication/         # Notification agent
│   ├── portfolio_dashboard/   # Analytics agent
│   ├── document_generator/    # Document generation agent
│   └── app_utils/             # Telemetry and utilities
├── api/                       # FastAPI REST API
│   └── main.py               # API endpoints
├── core/                      # Core business logic
│   └── storage.py            # Firestore client
├── .cloudbuild/              # CI/CD pipeline configs
│   ├── staging.yaml          # Staging deployment
│   ├── deploy-to-prod.yaml   # Production deployment
│   └── pr_checks.yaml        # Pull request checks
├── deployment/               # Infrastructure & deployment
│   ├── terraform/            # Terraform IaC
│   └── README.md             # Deployment guide
├── tests/                    # Unit and integration tests
├── Dockerfile                # Container configuration
├── Makefile                  # Development commands
├── pyproject.toml            # Python dependencies
└── README.md                 # This file
```

---

## Development Workflow

### 1. Local Development
```bash
# Install dependencies
make install

# Run API
make local-backend

# Or test in playground
make playground

# Run tests
make test
```

### 2. Make Changes
- Edit agent code in `agents/`
- Update API endpoints in `api/main.py`
- Add tests in `tests/`

### 3. Test & Lint
```bash
make test
make lint
```

### 4. Deploy to Dev
```bash
make deploy
```

### 5. Create Pull Request
- CI automatically runs `pr_checks.yaml`
- Linting, testing, and security checks
- Manual code review

### 6. Merge to Staging
- Auto-deploys via `staging.yaml`
- Load testing runs automatically
- On success, triggers production deployment

### 7. Production Deployment
- Manual approval gate
- Deployed via `deploy-to-prod.yaml`
- Rollback available if needed

---

## Common Tasks

### Add a New Agent

1. Create new directory in `agents/new_agent/`
2. Implement `NewAgent` class with `run()` method
3. Add tool function in `agents/agent.py`
4. Register tool with `root_agent`
5. Add API endpoint in `api/main.py`
6. Write tests in `tests/`

### Update Dependencies

```bash
# Add new package
uv add package-name

# Add dev dependency
uv add --dev package-name

# Update all packages
uv sync

# Lock dependencies
uv lock
```

### View Logs

```bash
# Local logs
tail -f *.log

# Cloud Run logs
gcloud logging read "resource.type=cloud_run_revision" \
  --project YOUR-PROJECT-ID \
  --limit 50
```

---

## Troubleshooting

### "Authentication failed" during deployment
```bash
gcloud auth login
gcloud auth application-default login
```

### "API not enabled" errors
```bash
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable artifactregistry.googleapis.com
```

### Local development not working
```bash
# Ensure you're using local mode
export GOOGLE_PROJECT_ID=local-dev

# Reinstall dependencies
rm -rf .venv
make install
```

### Docker build fails
```bash
# Ensure Docker is running
docker info

# Clear Docker cache
docker system prune -a
```

---

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Run `make lint` and `make test`
5. Submit pull request

---

## License

MIT License - see [LICENSE](LICENSE) for details

---

## Support

- **Issues:** [GitHub Issues](https://github.com/3piecechickendinner/LienOS/issues)
- **Documentation:** [Full docs](https://github.com/3piecechickendinner/LienOS/wiki)
- **Email:** sdhines3@gmail.com

---

## Acknowledgments

Built with:
- [Google Agent Development Kit (ADK)](https://github.com/google/adk)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Google Cloud Platform](https://cloud.google.com/)
- [Google Gemini AI](https://deepmind.google/technologies/gemini/)

**Powered by the Google Cloud Agent Starter Pack** - Production-ready deployment infrastructure for AI agents.
