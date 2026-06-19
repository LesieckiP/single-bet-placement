# Important
* Part A of the project is located within [part_a](./part_a/) directory
* You can see [my comments](./MY_COMMENTS.md) to understand some approaches i took and where i used the AI and why.

# Test Automation Project

## Prerequisites

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) package manager
- Chrome or Firefox browser installed

## Setup

1. Clone the repository and navigate to the project directory:
   ```bash
   git clone <repository-url>
   cd single-bet-placement
   ```

2. Install dependencies with uv:
   ```bash
   uv sync
   ```

3. Configure test settings in `resources/config.properties`:
   ```properties
   browser=chromium        # chromium or firefox
   app_url=https://qae-assignment-tau.vercel.app/
   api_url=https://qae-assignment-tau.vercel.app/api
   username=candidate-LfzI2CKDRw
   min_stake=1
   max_stake=100
   ```

## Running Tests

Run all tests:
```bash
uv run pytest
```

Run only API tests:
```bash
uv run pytest tests/api/
```

Run only WebUI tests:
```bash
uv run pytest tests/webui/
```

Run a specific test case by marker:
```bash
uv run pytest -m "tc('TC-03')"
```

## Linting

```bash
uv run ruff check --exclude .venv .
uv run ruff check --fix --exclude .venv .
```

## Project Structure

```
├── conftest.py                  # Session-scoped fixtures (browser, API session)
├── endpoints/                   # API client layer
│   ├── base_endpoint.py         # Base HTTP client with error handling
│   ├── bet_endpoint.py          # Betting API operations
│   └── models/                  # Pydantic response/request models
│       ├── balance_models.py
│       ├── bet_models.py
│       ├── error_models.py
│       └── matches_models.py
├── helper/
│   ├── browser_manager.py       # Selenium browser lifecycle
│   └── configuration_manager.py # Config properties reader
├── pages/                       # Page Object Model
│   ├── base_page.py             # Common Selenium helpers
│   ├── bet_slip.py              # Bet slip component
│   └── main_page.py             # Main app page
├── resources/
│   └── config.properties        # Test configuration
└── tests/
    ├── api/                     # API-level tests
    │   └── test_bet_placement_api.py
    └── webui/                   # Browser-based UI tests
        └── test_bet_placement.py
```
