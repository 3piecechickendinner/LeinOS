# LienOS

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Status](https://img.shields.io/badge/Status-Production%20Ready-green.svg)
![Deployment](https://img.shields.io/badge/Deployed-Google%20Cloud%20Run-4285F4.svg)

**AI-Powered Tax Lien Portfolio Management System**

LienOS is an intelligent multi-agent system that automates tax lien investment operations. Unlike passive tracking tools, LienOS employs proactive AI agents that monitor deadlines, calculate interest, process payments, and generate documents—all without manual intervention.

## 🚀 Live Production Deployment

### Backend API (Google Cloud Run)

**Production API:** https://lien-os-402756129398.us-central1.run.app

- **Swagger Docs:** https://lien-os-402756129398.us-central1.run.app/docs
- **ReDoc:** https://lien-os-402756129398.us-central1.run.app/redoc
- **Health Check:** https://lien-os-402756129398.us-central1.run.app/health

The API is deployed on **Google Cloud Run** with auto-scaling, high availability, and production-grade observability.

### Frontend (Render)

**Frontend URL:** Deploy using the instructions below to get your Render URL

The React frontend is deployed as a static site on **Render** and connects to the Cloud Run backend. See [Deploy Frontend to Render](#deploy-frontend-to-render) for setup instructions.

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

### Load Sample Data

To populate your Firestore database with realistic mock data for testing:

```bash
# Ensure GOOGLE_PROJECT_ID is set in .env
# Default tenant: demo-user
python scripts/load_mock_data.py

# Or specify a custom tenant ID
python scripts/load_mock_data.py my-tenant-id
```

This will create:
- **12 tax liens** with varied statuses, amounts, and dates
- **4 redemption deadlines** at different intervals
- **Payment records** for redeemed liens

**Sample output:**
```
====================================================================
LienOS Mock Data Loader
====================================================================

Project ID: valid-perigee-480016-f3
Tenant ID: demo-user

📦 Initializing Firestore connection...
✓ Connected to Firestore

🏠 Generating mock lien data...
📝 Creating 12 liens...
  ✓ [ 1/12] MI-2024-1000          - $ 8,500 (ACTIVE)
  ✓ [ 2/12] BR-2024-1001          - $12,000 (ACTIVE)
  ...
  💰 [11/12] BR-2023-1010          - $ 7,800 (REDEEMED)
  💰 [12/12] PA-2023-1011          - $ 3,500 (REDEEMED)

✓ Created 12 liens

⏰ Creating deadlines...
  ⏰ [1/4] redemption              - Due in  30 days
  ⏰ [2/4] notice_required         - Due in  60 days
  ⏰ [3/4] interest_calculation    - Due in  90 days
  ⏰ [4/4] annual_review           - Due in 120 days

✓ Created 4 deadlines

💵 Creating payment records for redeemed liens...
  💰 [1/2] Redemption payment: $ 8,234.52
  💰 [2/2] Redemption payment: $ 3,789.33

✓ Created 2 payment records

====================================================================
📊 SUMMARY
====================================================================

✓ Loaded 12 total liens
  • 10 ACTIVE liens
  • 2 REDEEMED liens
  • Total invested: $87,500.00

✓ Loaded 4 deadlines
✓ Loaded 2 payment records

🎉 Mock data successfully loaded for tenant 'demo-user'!
```

**Access the data:**
- Set `X-Tenant-ID: demo-user` header in API requests
- View in Swagger UI: https://lien-os-402756129398.us-central1.run.app/docs
- Query in frontend with matching tenant ID

---

## API Documentation

Interactive API documentation is available:
- **Production:** https://lien-os-402756129398.us-central1.run.app/docs
- **Local:** http://localhost:8000/docs

### Example API Calls

**Create a Lien:**
```bash
# Production
curl -X POST https://lien-os-402756129398.us-central1.run.app/api/liens \
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

# Local
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

### Deploy Frontend to Render

The React frontend is deployed to Render as a static site and connects to the production Cloud Run backend.

#### Automated Deployment with render.yaml

LienOS includes a `render.yaml` Blueprint configuration for one-click deployment to Render:

1. **Fork or push this repository to GitHub**

2. **Create a new Static Site on Render:**
   - Go to [Render Dashboard](https://dashboard.render.com/)
   - Click "New" → "Blueprint"
   - Connect your GitHub repository
   - Render will automatically detect the `render.yaml` file

3. **Automatic configuration:**
   - Build command: `cd frontend && npm install && npm run build`
   - Publish directory: `frontend/dist`
   - Environment variable `VITE_API_URL` is pre-configured to point to the Cloud Run backend

4. **Your frontend will be live at:** `https://lienos-frontend.onrender.com` (or your custom domain)

#### Manual Deployment (Alternative)

If you prefer manual setup:

```bash
# From the Render Dashboard
# 1. New → Static Site
# 2. Connect your repository
# 3. Configure:
#    - Name: lienos-frontend
#    - Build command: cd frontend && npm install && npm run build
#    - Publish directory: frontend/dist
#    - Environment variable: VITE_API_URL=https://lien-os-402756129398.us-central1.run.app
```

#### Frontend Configuration

The frontend automatically:
- Uses **mock data in development** mode (`npm run dev`)
- Connects to **production API in production** builds (`npm run build`)
- Handles client-side routing with React Router
- Includes security headers (X-Frame-Options, CSP, etc.)

**Local development:**
```bash
cd frontend
npm install
npm run dev  # Runs on http://localhost:3000 with API proxy
```

**Production build (manual):**
```bash
cd frontend
npm run build  # Creates optimized build in dist/
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
