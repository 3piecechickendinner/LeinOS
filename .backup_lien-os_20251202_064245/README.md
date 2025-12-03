# LienOS

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Status](https://img.shields.io/badge/Status-In%20Development-yellow.svg)

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

### Tech Stack

- **AI Framework:** Google ADK + Gemini 2.0 Flash
- **Backend:** FastAPI (async Python)
- **Database:** Google Firestore (with local dev mode)
- **Validation:** Pydantic v2
- **Testing:** Pytest + pytest-asyncio

### Design Principles

- **Multi-tenant:** Complete data isolation per tenant
- **Agent-first:** Business logic lives in specialized agents
- **Async throughout:** Non-blocking operations for scale
- **Local-first development:** Works without cloud credentials

---

## Quick Start

### Prerequisites

- Python 3.11+
- pip

### Installation

```bash
# Clone the repository
git clone https://github.com/3piecechickendinner/LienOS.git
cd lien-os

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Run the API

```bash
# Start the development server
uvicorn api.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`

### Run Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_agents.py -v

# Run with coverage
pytest tests/ --cov=.
```

---

## API Documentation

Interactive API documentation is available when the server is running:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

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

**Check Deadlines:**
```bash
curl -X POST http://localhost:8000/api/deadlines/check \
  -H "X-Tenant-ID: my-tenant-id"
```

---

## Agent Details

### LienTrackerAgent
The core CRUD agent for managing tax lien records. Handles creation, retrieval, updates, listing with filters, and soft/hard deletion. Automatically creates associated deadlines when liens are added.

### InterestCalculatorAgent
Calculates accrued interest based on purchase amount, interest rate, and days elapsed. Supports simple interest calculation with plans for state-specific compound interest rules.

### DeadlineAlertAgent
Monitors redemption deadlines and sends alerts at configured intervals (default: 90, 60, 30, 14, 7, 3, 1 days before). Creates notifications that can be delivered via email, SMS, or in-app.

### PaymentMonitorAgent
Records payments against liens, calculates remaining balance, and automatically marks liens as REDEEMED when fully paid. Creates payment notifications and supports payment verification and reconciliation.

### CommunicationAgent
Manages the notification system including in-app alerts, email queue, and SMS queue. Handles marking notifications as read and provides filtering by type, priority, and read status.

### PortfolioDashboardAgent
Provides comprehensive portfolio analytics including total invested, interest earned, ROI calculations, and breakdowns by status/county. Generates actionable recommendations and calculates a portfolio health score.

### DocumentGeneratorAgent
Generates HTML documents including redemption notices, portfolio reports, payment receipts, and 1099-INT style tax summaries. Documents include proper formatting and can be extended to PDF generation.

---

## Development

### Local vs Production Mode

LienOS automatically detects its environment:

**Local Development (default):**
- Uses in-memory storage (data resets on restart)
- No Google Cloud credentials needed
- Set `GOOGLE_PROJECT_ID=local-dev` or leave unset

**Production:**
- Uses Google Firestore
- Requires `GOOGLE_APPLICATION_CREDENTIALS`
- Set `GOOGLE_PROJECT_ID` to your GCP project

### Environment Variables

Create a `.env` file in the project root:

```env
# Required for production
GOOGLE_PROJECT_ID=your-gcp-project-id
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json

# Optional
LOG_LEVEL=INFO
```

### Project Structure

```
lien-os/
├── api/
│   └── main.py              # FastAPI application
├── agents/
│   ├── interest_calculator/ # Interest calculation agent
│   ├── deadline_alert/      # Deadline monitoring agent
│   ├── payment_monitor/     # Payment processing agent
│   ├── lien_tracker/        # Lien CRUD agent
│   ├── communication/       # Notification agent
│   ├── portfolio_dashboard/ # Analytics agent
│   └── document_generator/  # Document generation agent
├── core/
│   ├── base_agent.py        # Base agent class
│   ├── data_models.py       # Pydantic models
│   └── storage.py           # Storage abstraction
├── tests/
│   ├── conftest.py          # Pytest fixtures
│   ├── test_agents.py       # Agent unit tests
│   └── test_api.py          # API integration tests
├── requirements.txt
└── README.md
```

### Testing Guidelines

- All tests use local storage mode (no cloud dependencies)
- Use `pytest-asyncio` for async test functions
- Create fixtures in `conftest.py` for reusable test data
- Aim for >80% code coverage
- Run tests before committing: `pytest tests/ -v`

---

## Roadmap

### Completed
- [x] Core infrastructure (storage, base agent, data models)
- [x] 7 AI agents with full capabilities
- [x] FastAPI REST API with 25+ endpoints
- [x] Comprehensive test suite (60+ tests)
- [x] Local development mode (no cloud needed)
- [x] Multi-tenant security enforcement

### In Progress
- [ ] MCP tool integrations (SendGrid, Twilio, Google Calendar)
- [ ] State-specific interest calculation rules
- [ ] PDF document generation (reportlab)

### Planned
- [ ] Frontend UI (React/Next.js)
- [ ] User authentication (Firebase Auth)
- [ ] Scheduled jobs (Cloud Scheduler)
- [ ] Docker containerization
- [ ] CI/CD pipeline (GitHub Actions)
- [ ] Production deployment (Cloud Run)
- [ ] Mobile app (React Native)

---

## Contributing

We welcome contributions! Here's how to get started:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Run tests: `pytest tests/ -v`
5. Commit: `git commit -m 'Add amazing feature'`
6. Push: `git push origin feature/amazing-feature`
7. Open a Pull Request

### Code Style

- Follow PEP 8 guidelines
- Use type hints for all function signatures
- Write docstrings for classes and public methods
- Keep functions focused and under 50 lines

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Acknowledgments

- Built with [Google Agent Development Kit (ADK)](https://github.com/google/adk-python)
- Powered by [Gemini 2.0 Flash](https://deepmind.google/technologies/gemini/)
- API framework: [FastAPI](https://fastapi.tiangolo.com/)

---

<p align="center">
  <strong>LienOS</strong> — Intelligent Tax Lien Management
</p>
