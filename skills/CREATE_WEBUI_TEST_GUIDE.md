# Create WebUI Test Skill - Installation & Usage Guide

## Overview

The `create-webui-test` skill is a Claude Code slash command that automates the implementation of WebUI test cases from the project's test plan. When invoked, it:

1. Analyzes `part_a/TESTPLAN.md` to identify unautomated test cases
2. Prioritizes them by severity (Critical > High > Medium > Low) and WebUI relevance
3. Implements the highest-priority test following the project's Page Object Model patterns
4. Validates with static analysis (ruff) and test execution (pytest)
5. Marks the test case as automated in the test plan
6. Creates a pull request targeting `ai-playground`

## Prerequisites

- **Claude Code CLI** installed and configured ([installation guide](https://docs.anthropic.com/en/docs/claude-code))
- **Python 3.13+** with [uv](https://docs.astral.sh/uv/) package manager
- **Chrome browser** installed (Selenium WebDriver target)
- **Git** configured with push access to the repository
- **GitHub CLI** (`gh`) authenticated for PR creation
- The `ai-playground` branch available locally and on remote

## Installation

The skill is shipped with this repository. No additional installation is needed.

**Skill location:** `.claude/commands/create-webui-test.md`

If setting up from a fresh clone:

```bash
git clone <repository-url>
cd single-bet-placement
uv sync
```

The `.claude/commands/` directory is tracked in git, so the skill is available immediately after cloning.

## Usage

### Invoking the Skill

Open Claude Code in the project root and type:

```
/create-webui-test
```

Claude will then walk through the full process: analyzing the test plan, picking a test case, implementing it, validating, and creating a PR.

### What Happens During Execution

| Phase | What Claude Does |
|---|---|
| **Analysis** | Reads `TESTPLAN.md`, scans `tests/webui/` for `@pytest.mark.tc()` markers |
| **Selection** | Announces which test case it will implement and why |
| **Branching** | Creates `test/tc-XX-<description>` from `ai-playground` |
| **Implementation** | Writes the test file, extends page objects as needed |
| **Validation** | Runs `uv run ruff check` and `uv run pytest` on the new test |
| **Bookkeeping** | Adds `**Automation Status:** Automated` to the test case in TESTPLAN.md |
| **PR creation** | Commits, pushes, and opens a PR against `ai-playground` |

### What the Skill Produces

Each invocation creates:

- A new test file in `tests/webui/` (or extends an existing one)
- Page object additions in `pages/` if new UI interactions are needed
- An updated `part_a/TESTPLAN.md` with the automation status marker
- A git feature branch and a GitHub pull request

## Project Patterns the Skill Follows

The skill is designed to match the existing codebase conventions exactly:

### Page Object Model

```
pages/
  base_page.py        # Generic Selenium helpers (find, click, type, wait)
  main_page.py        # Locators + methods for the main page
  bet_slip.py         # Locators + methods for the bet slip component
```

- Locators are class-level tuples: `ELEMENT = (By.ID, "element-id")`
- Methods delegate to `BasePage` helpers
- New components get their own file inheriting from `BasePage`

### API Layer

```
endpoints/
  base_endpoint.py    # HTTP methods + error handling
  bet_endpoint.py     # Betting domain operations
  models/             # Pydantic request/response models
```

### Test Structure

```
tests/webui/
  test_bet_placement.py   # TC-02, TC-03
  test_double_submit.py   # TC-01 (created by this skill)
```

- Class-based tests with `@pytest.mark.tc("TC-XX")` markers
- `@pytest.fixture(autouse=True, scope="class")` for setup/teardown
- API-driven test data management (reset balance, place setup bets)
- Descriptive assertion messages

## Manual Verification After Skill Completion

After the skill creates a PR, the QA engineer should:

1. **Review the PR diff** — verify the test assertions match the expected results in TESTPLAN.md
2. **Check page object changes** — ensure new locators and methods follow existing naming patterns
3. **Verify the test passed** — check the skill's console output for pytest results
4. **Review money-correctness assertions** — per TESTPLAN.md Section 13, AI output on money assertions must be human-verified

## Troubleshooting

| Issue | Resolution |
|---|---|
| `/create-webui-test` not found | Ensure you are in the project root and `.claude/commands/create-webui-test.md` exists |
| No unautomated WebUI test cases | All WebUI-relevant test cases may be covered; check TESTPLAN.md for remaining API-only cases |
| Test fails during validation | Check if the test environment is reachable (`https://qae-assignment-tau.vercel.app/`); reset balance manually if corrupted |
| Ruff check fails | The skill attempts auto-fix; if issues persist, fix manually and re-run |
| Chrome not found | Install Chrome or switch to Firefox in `resources/config.properties` |
| Branch already exists | Delete the existing branch (`git branch -D test/tc-XX-...`) or use a unique name |
| `gh` not authenticated | Run `gh auth login` to authenticate GitHub CLI |

## Extending the Skill

To adapt this skill for API tests:

1. Copy `.claude/commands/create-webui-test.md` to `.claude/commands/create-api-test.md`
2. Change the target directory from `tests/webui/` to `tests/api/`
3. Update the test template to use `BetEndpoint` directly instead of page objects
4. Adjust prioritization to prefer API-focused test cases
