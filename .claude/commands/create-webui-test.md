# Create WebUI Test

Automate the next highest-priority WebUI test case from the test plan. Follow this process step by step.

## Step 1: Analyze Test Plan and Existing Coverage

1. Read `part_a/TESTPLAN.md` to identify all test cases with their priorities and steps
2. Scan `tests/webui/` for existing automated tests — look for `@pytest.mark.tc()` markers to map which test case IDs are already covered
3. Build a prioritized list of unautomated test cases:
   - **Critical** before High before Medium before Low
   - Among same priority, prefer test cases with explicit WebUI steps over API-only ones
   - Skip test cases that are purely API-focused (direct those to `tests/api/` instead)
4. Select the top-priority unautomated WebUI test case and announce which one you are implementing

## Step 2: Create a Feature Branch

Create a branch from `ai-playground`:

```
git checkout -b test/tc-XX-short-description ai-playground
```

Use the test case ID and a short kebab-case description in the branch name.

## Step 3: Implement the Test

Follow the project's established OOP patterns exactly:

### Page Object Model

- **BasePage** (`pages/base_page.py`): Generic element interactions (find, click, type, waits). If the test needs a new generic Selenium action (e.g. double-click, drag-and-drop), add it here with a locator parameter and `WebDriverWait` + `expected_conditions`.
- **Page-specific classes** (`pages/main_page.py`, `pages/bet_slip.py`): Wrap locators as class-level tuples `(By.X, "selector")`. Add page-specific methods that delegate to `BasePage` methods. Each method does one UI action or read.
- If a new page/component is needed (e.g., a receipt modal, error modal), create a new file in `pages/` inheriting from `BasePage`.

### API Layer

- Use `BetEndpoint` (`endpoints/bet_endpoint.py`) for server-side operations: `reset_balance()`, `get_balance()`, `get_matches()`, `place_bet()`.
- Use Pydantic models from `endpoints/models/` for type-safe request/response handling.

### Test File Structure

Create a new file in `tests/webui/` named `test_<descriptive_name>.py`:

```python
import pytest
from selenium.webdriver.remote.webdriver import WebDriver

from endpoints.bet_endpoint import BetEndpoint
from pages.bet_slip import BetSlipPage
from pages.main_page import MainPage


@pytest.fixture(autouse=True, scope="class")
def setup_and_teardown(request, web_app, api_session):
    """<Describe what this fixture sets up>"""
    bet_endpoint = BetEndpoint(api_session)
    request.cls.main_page = MainPage(web_app)
    request.cls.bet_slip_page = BetSlipPage(web_app)
    request.cls.bet_endpoint = bet_endpoint
    request.cls.driver = web_app

    # Reset balance to known state
    bet_endpoint.reset_balance()
    request.cls.initial_balance = bet_endpoint.get_balance().balance

    # Refresh page to ensure clean UI state
    web_app.refresh()

    yield

    bet_endpoint.reset_balance()


class Test<DescriptiveName>:
    main_page: MainPage
    bet_slip_page: BetSlipPage
    bet_endpoint: BetEndpoint
    driver: WebDriver
    initial_balance: float

    @pytest.mark.tc("TC-XX")
    def test_<descriptive_name>(self):
        """TC-XX: <One-line description matching the test plan>"""
        # Test implementation
        ...
```

### Conventions

- Ruff linting: line-length=160, E/F/I rules, double-quote strings
- Type annotations on class attributes injected by fixtures
- Descriptive assertion messages explaining what went wrong
- Use `pytest.approx()` for floating-point comparisons (monetary values)
- Use API (`BetEndpoint`) for ground-truth verification of balances and bet state
- Use `time.sleep()` sparingly and only when waiting for async server processing in timing-sensitive tests

## Step 4: Validate

Run both checks and fix any issues before proceeding:

```bash
uv run ruff check --exclude .venv .
uv run ruff check --fix --exclude .venv .
uv run pytest tests/webui/<new_test_file>.py -v
```

If the test fails, diagnose and fix the issue. Re-run until green.

## Step 5: Update Test Plan

In `part_a/TESTPLAN.md`, add to the implemented test case:

```
- **Automation Status:** Automated (`tests/webui/<test_file>.py`)
```

## Step 6: Commit and Create PR

1. Stage all changed and new files
2. Commit with a descriptive message
3. Push the branch
4. Create a PR targeting `ai-playground`:

```bash
gh pr create --base ai-playground --title "Test: TC-XX <short description>" --body "..."
```

## Key Reference Files

| File | Purpose |
|---|---|
| `part_a/TESTPLAN.md` | Test case definitions and priorities |
| `tests/webui/` | WebUI test directory |
| `pages/base_page.py` | Base page object (generic Selenium helpers) |
| `pages/main_page.py` | Main page (balance, odds buttons) |
| `pages/bet_slip.py` | Bet slip (stake input, place bet button) |
| `endpoints/bet_endpoint.py` | API client for betting operations |
| `endpoints/models/` | Pydantic request/response models |
| `conftest.py` | Session-scoped fixtures (browser, API session) |
| `resources/config.properties` | Test configuration (URLs, credentials, stake limits) |

## Test Environment

- App URL: `https://qae-assignment-tau.vercel.app/`
- API URL: `https://qae-assignment-tau.vercel.app/api`
- Test user: `candidate-LfzI2CKDRw`
- API docs: `/api/docs` (Swagger UI)
