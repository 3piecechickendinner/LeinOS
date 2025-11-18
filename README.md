# LienOS - AI-Powered Tax Lien Management Platform

Production-ready, multi-tenant SaaS platform for automating tax lien investment operations using Google's Agent Development Kit (ADK).

## Overview

LienOS is a comprehensive platform that automates tax lien management workflows through intelligent AI agents. Built with Google's Gemini models and Firestore, it provides secure, scalable multi-tenant infrastructure for managing tax lien portfolios, calculating interest, processing payments, and generating insights.

## Tech Stack

- **Python 3.11+** - Core language
- **Google Agent Development Kit (ADK)** - Agent framework
- **Google Gemini 2.0 Flash** - AI model for agent reasoning
- **Google Cloud Firestore** - Multi-tenant data storage
- **Pydantic** - Data validation and serialization
- **Python-dotenv** - Environment configuration

## Project Structure

```
lien-os/
├── core/                    # Core platform functionality
│   ├── base_agent.py        # Base agent class for all agents
│   ├── data_models.py       # Pydantic models (Lien, Payment, etc.)
│   └── storage.py           # Firestore client with multi-tenant security
├── agents/                  # Agent implementations
│   └── interest_calculator/ # Interest calculation agent
│       └── agent.py
├── shared_tools/            # Shared tools and utilities
├── tests/                   # Test suite
├── test_interest_calculator.py  # Quick test script
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd lien-os
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   cp .env.example .env
   ```

5. **Configure your `.env` file** with your Google Cloud credentials (see Configuration section below).

## Configuration

Create a `.env` file in the root directory with the following variables:

```bash
# Google Cloud Configuration
GOOGLE_CLOUD_PROJECT_ID=your-project-id

# Google Gemini API
GOOGLE_AI_API_KEY=your-gemini-api-key

# Optional: Logging level
LOG_LEVEL=INFO
```

### Setting up Google Cloud

1. **Create a Google Cloud Project:**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select an existing one
   - Note your Project ID

2. **Enable required APIs:**
   - Enable Firestore API
   - Enable Gemini API (or Vertex AI API)

3. **Set up authentication:**
   - Create a service account with Firestore permissions
   - Download the JSON key file
   - Set `GOOGLE_APPLICATION_CREDENTIALS` environment variable to the path of your key file:
     ```bash
     export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/key.json"
     ```

4. **Get Gemini API Key:**
   - Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create an API key
   - Add it to your `.env` file

## Current Status

🚧 **In Development** - Core infrastructure and Interest Calculator Agent complete

### ✅ Completed

- Multi-tenant Firestore storage layer with security enforcement
- Base agent architecture (`LienOSBaseAgent`)
- Data models (Lien, Payment, InterestCalculation, AgentContext)
- Interest Calculator Agent
- Test infrastructure

### 🚧 In Progress

- Additional specialized agents (see Roadmap)

## Roadmap

The platform will include 7 specialized AI agents:

1. **Interest Calculator Agent** ✅ - Calculates accrued interest on tax liens
2. **Payment Processor Agent** - Handles lien redemption payments and updates
3. **Lien Status Monitor Agent** - Tracks lien status changes and deadlines
4. **Portfolio Analyzer Agent** - Provides portfolio-level insights and analytics
5. **Risk Assessment Agent** - Evaluates lien risk factors and recommendations
6. **Document Generator Agent** - Generates reports, statements, and legal documents
7. **Notification Agent** - Sends alerts for deadlines, payments, and status changes

## Usage Example

```python
import asyncio
from core.storage import FirestoreClient
from agents.interest_calculator.agent import InterestCalculatorAgent

async def main():
    # Initialize storage
    storage = FirestoreClient(project_id="your-project-id")
    
    # Create agent
    agent = InterestCalculatorAgent(storage=storage)
    
    # Run interest calculation
    result = await agent.run(
        tenant_id="tenant_123",
        task="calculate_interest",
        lien_ids=["lien_id_456"]
    )
    
    print(f"Interest accrued: ${result['interest_accrued']:.2f}")

asyncio.run(main())
```

## Testing

Run the test script to verify the Interest Calculator Agent:

```bash
python test_interest_calculator.py
```

## Multi-Tenancy

LienOS enforces strict tenant isolation at the storage layer. All data operations automatically filter by `tenant_id`, ensuring that tenants can only access their own data. This is enforced in:

- Document creation
- Document retrieval
- Document updates
- Query operations

## Contributing

Contributions are welcome! Please ensure:

- Code follows PEP 8 style guidelines
- All tests pass
- New features include appropriate tests
- Documentation is updated

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Author

S.D. - 2024
