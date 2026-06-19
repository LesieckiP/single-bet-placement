# Test Plan: Single Bet Placement

**Document type:** Test Plan (structured per ISTQB CTFL test planning content, IEEE 829-aligned)
**Feature under test:** Single Bet Placement
**Source document:** Feature_Specification.pdf (revision from date 18.06.2026)
**Author:** Piotr L
**Date:** 2026-06-18
**Status:** Draft v1.1

---

## 1. Introduction / Objectives

This feature lets a customer wager real money on a pre-match football outcome. It is new core functionality for the business, so two things must both hold before release:

1. **Correctness for the user** — odds, stake, payout, and bet state shown to the customer must always be accurate and consistent with what is actually recorded server-side.
2. **Financial integrity for the company** — no path through the UI or API may produce a bet, payout, or balance change that does not match business rules. Every money-affecting action must be validated, atomic, and resistant to tampering, duplication, or race conditions. 

Testing is scoped to verify both, with money-leak prevention treated as a release-blocking concern, not a secondary one.

## 2. Scope

### 2.1 In scope
- Match list display and odds selection
- Bet slip behavior: selection, stake entry, balance, potential payout, removal
- Place Bet interaction and state transitions: idle → loading → success/failure
- Success receipt content and dismissal flow
- Error modal content, Rebet/Close/X behavior
- Date and odds filters
- All business rules and validation rules
- Backend API: matches, balance, place-bet, reset-balance endpoints, auth header, error classes
- Functional, negative, boundary, security, and data-integrity testing across UI and API layers

### 2.2 Out of scope
- Live betting
- Multi-bets / accumulators
- Sports other than football/soccer
- Mobile-specific UX
- Payment provider / deposit-withdrawal flows (not part of this feature)

## 3. Test Items

| Item | Description |
|---|---|
| Web UI | Match list, bet slip, receipt modal, error modal, filters |
| API | Matches, balance, place-bet, reset-balance endpoints |
| API documentation | Swagger UI |

## 4. Test Approach / Strategy

| Level | Technique | Notes |
|---|---|---|
| UI functional | Black-box, state transition testing | Bet slip and modal states form a defined state machine (idle/selected → loading → success/failure) |
| Boundary value analysis | Stake and odds limits, decimal precision | Direct mapping to the Business Rules table |
| Negative / validation testing | Missing fields, wrong types, malformed JSON, invalid enum, unknown IDs | Per the Validation Rules tables |
| API / contract testing | Request/response schema, status codes, headers | Verify UI and API enforce the same rules independently (defense in depth) |
| Security & abuse testing | Tampering, replay, race conditions, auth bypass | See Section 6 (security-focused scenarios) |
| Concurrency testing | Double-submit, simultaneous requests for same user | Validates duplicate-bet prevention |
| Data integrity / consistency | Balance before/after, reset behavior, persisted vs returned state | Persisted state must match the response after every money-affecting call |
| Exploratory | Free-form session on bet slip and modals | Time-boxed, post-scripted-test-pass |

Both **UI-layer** and **API-layer** validation are tested independently, since the spec explicitly requires enforcement at both layers — a defect where the UI blocks something the API silently accepts (or vice versa) is treated as a critical finding, because it represents a potential money leak.

## 5. Test Scenarios (Traceability Summary)

Each scenario below carries a `Spec Ref` for traceability back to the Feature Specification. If the spec is revised, re-validate these references as part of the update — they are intentionally kept only in this table so the rest of the document doesn't need rewriting when section numbers shift.

Fields: **ID and Title**, **Spec Ref**, **Priority**, **Risk Rationale**, **Steps**, **Expected Result**.

---
#### TC-01: Double-submit / race condition produces one bet
- **Spec Ref:** 2.3 / 5.3
- **Priority:** Critical
- **Risk Rationale:** The single highest-impact money-leak scenario — a race condition on submit could duplicate a real-money bet from one user action.
- **Steps:** 1. Fire two near-simultaneous `place-bet` requests for the same user/selection/stake. 2. Also test rapid double-click in the UI.
- **Expected Result:** Exactly one bet is created and one stake deducted; the second request returns 409.
- **Automation Status:** Automated — WebUI rapid double-click (`tests/webui/test_double_submit.py`). Marked `xfail`: test confirms a race condition where double-click inconsistently creates two bets instead of one.

#### TC-02: Successful placement deducts stake exactly once
- **Spec Ref:** 2.3 / 2.4
- **Priority:** Critical
- **Risk Rationale:** Core money-correctness assertion — incorrect or duplicate deduction is a direct financial leak.
- **Steps:** 1. Record balance. 2. Place a valid bet of known stake. 3. Re-check balance via UI and `GET /api/balance`.
- **Expected Result:** Balance decreases by exactly the stake amount, once, and matches across UI and API.
- **Automation Status:** Automated (`tests/webui/test_bet_placement.py`)

#### TC-03: Stake exceeding balance
- **Spec Ref:** 3 / 4.1
- **Priority:** Critical
- **Risk Rationale:** Allowing a bet beyond available balance is a direct path to a negative balance / money leak.
- **Steps:** 1. Note current balance. 2. Attempt a stake greater than balance via UI. 3. Repeat via direct API call.
- **Expected Result:** Rejected at both layers with "Insufficient balance" messaging; balance is unchanged.
- **Automation Status:** Automated (`tests/webui/test_bet_placement.py`)

#### TC-04: Missing/invalid user context
- **Spec Ref:** 4.3 / 5.1
- **Priority:** Critical
- **Risk Rationale:** Weak auth-context handling can allow unauthenticated or misattributed bets.
- **Steps:** 1. Call `place-bet` with no `user-id` header. 2. Call with an empty/malformed value.
- **Expected Result:** 401 returned in both cases; no bet created.

#### TC-05: Client-supplied odds are ignored
- **Spec Ref:** 5.3
- **Priority:** Critical
- **Risk Rationale:** If the server trusted a client-supplied odds value, an attacker could win a hugely inflated payout for a trivial stake.
- **Steps:** Submit a `place-bet` request with an extra `odds` field set far above the real match odds.
- **Expected Result:** Server uses its own authoritative odds; payout reflects true odds, not the submitted value.

#### TC-06: Auth bypass via missing/malformed user context
- **Spec Ref:** 5.1
- **Priority:** Critical
- **Risk Rationale:** Any path that processes a bet without a valid user context is an unattributed financial transaction.
- **Steps:** Call `place-bet` and `balance` with missing, empty, and malformed `user-id`.
- **Expected Result:** All rejected with 401; no state change.

#### TC-07: Negative stake accepted by API
- **Spec Ref:** 3 / 4.1
- **Priority:** Critical
- **Risk Rationale:** A negative stake inverts the payout direction — the house pays out on a "loss" and collects nothing on a "win." This is a direct financial exploit path.
- **Steps:** 1. Send `POST /api/place-bet` with a valid match/selection but a negative stake (e.g. `-5`). 2. Repeat with `-0.01` and `0`.
- **Expected Result:** All rejected with a 4xx error (stake must be between min and max per Business Rules). Balance unchanged.

#### TC-08: Balance cannot go negative through repeated betting
- **Spec Ref:** 3 / 4.1
- **Priority:** Critical
- **Risk Rationale:** If the server does not atomically check balance before deducting, rapid sequential bets can overdraw the account — a direct financial exposure.
- **Steps:** 1. Reset balance. 2. Place valid bets in rapid succession (each at a stake near the total balance) via API. 3. Check final balance via `GET /api/balance`.
- **Expected Result:** Balance never falls below zero; once funds are insufficient, further bets are rejected with "Insufficient balance."

#### TC-09: Success receipt displays correct bet details
- **Spec Ref:** 2.3 / 2.4
- **Priority:** High
- **Risk Rationale:** Showing the user incorrect payout, odds, or match info in the receipt undermines trust and may violate regulatory requirements for transparent bet confirmation.
- **Steps:** 1. Reset balance. 2. Note a match's teams, odds for the chosen selection. 3. Select odds, enter a known stake, place the bet. 4. Read the confirmation pop-up's match name, selection, stake, odds, and payout. 5. Cross-check payout against API response and against the formula: payout = stake × odds.
- **Expected Result:** All fields in the receipt match the pre-submission bet slip values and the API response. Payout equals stake × odds (not doubled, not truncated).

#### TC-10: Bet slip displays correct potential payout before placement
- **Spec Ref:** 2.2 / 3
- **Priority:** High
- **Risk Rationale:** A wrong payout preview misleads the user about expected returns before they commit real money — a trust and compliance issue.
- **Steps:** 1. Select an outcome with known odds. 2. Enter a stake. 3. Read the "Potential Payout" value displayed in the bet slip. 4. Compute expected payout = stake × odds.
- **Expected Result:** Displayed potential payout matches stake × odds, rounded per business rules.

#### TC-11: Stake at minimum boundary
- **Spec Ref:** 3 / 4.1
- **Priority:** High
- **Risk Rationale:** Boundary value analysis — off-by-one on the minimum stake could allow zero-value bets (no revenue) or reject valid minimum bets (lost conversion). Note: min stake value is pending clarification (€1.00 vs €1.01, see Section 14).
- **Steps:** 1. Via UI: select an outcome, enter exactly the minimum stake, attempt to place bet. 2. Via API: send `place-bet` with stake = minimum. 3. Repeat with stake = minimum − 0.01.
- **Expected Result:** Minimum stake is accepted at both layers; stake below minimum is rejected with appropriate validation message. Both layers agree on the boundary.

#### TC-12: Stake at maximum boundary
- **Spec Ref:** 3 / 4.1
- **Priority:** High
- **Risk Rationale:** Boundary value analysis — if the maximum stake boundary is not enforced identically at UI and API layers, an attacker could bypass the UI limit and place an oversized bet via direct API call.
- **Steps:** 1. Reset balance to ensure it exceeds max stake. 2. Via UI: enter stake = €100.00 (max), verify acceptance. Enter stake = €100.01, verify rejection. 3. Via API: repeat both calls.
- **Expected Result:** €100.00 accepted; €100.01 rejected with "Maximum stake is €100.00" (or equivalent). Both layers enforce the same boundary.

#### TC-13: Error modal on bet failure — content and interaction
- **Spec Ref:** 2.3
- **Priority:** High
- **Risk Rationale:** If the error modal auto-dismisses too quickly or lacks a retry path, users cannot recover from transient failures and may abandon the flow — impacting conversion and trust.
- **Steps:** 1. Trigger a bet placement error (e.g. by rapid double-click producing a conflict, or by engineering insufficient balance mid-flow). 2. Observe the error modal: read its message text. 3. Attempt to interact with Rebet / Close / X buttons before auto-dismiss.
- **Expected Result:** Error modal is displayed long enough for the user to read and act. Modal contains a clear error message. Close/X dismisses the modal. Rebet (if present) returns user to the bet slip with prior selection/stake intact.

#### TC-14: Success receipt dismissal resets bet slip to idle
- **Spec Ref:** 2.3 / 2.4
- **Priority:** High
- **Risk Rationale:** If dismissing the receipt does not reset the bet slip state, the user may accidentally re-submit the same bet or see stale data — directly linked to duplicate-bet risk.
- **Steps:** 1. Place a valid bet successfully. 2. Dismiss the confirmation pop-up (Close / X / click outside). 3. Inspect the bet slip state.
- **Expected Result:** Bet slip returns to idle/empty state — no prior selection, no stake value, no payout shown. User must start a new selection to place another bet.

#### TC-15: Reset-balance returns consistent value with get-balance
- **Spec Ref:** N/A (test infrastructure)
- **Priority:** High
- **Risk Rationale:** Test reliability depends on reset-balance producing a known starting state. If reset-balance and get-balance disagree, every subsequent test assertion on balance is unreliable.
- **Steps:** 1. Call `POST /api/reset-balance`, record the returned balance. 2. Immediately call `GET /api/balance`, record the returned balance. 3. Repeat 3 times.
- **Expected Result:** Both endpoints return the same balance value on every iteration.

#### TC-16: Place-bet with missing required fields
- **Spec Ref:** 4.1 / 4.2
- **Priority:** High
- **Risk Rationale:** If the API silently defaults a missing required field (e.g. defaulting selection to HOME), it can produce a bet the user never intended — a correctness and liability issue.
- **Steps:** 1. Send `POST /api/place-bet` with missing `matchId`. 2. Repeat with missing `selection`. 3. Repeat with missing `stake`. 4. Repeat with empty body `{}`.
- **Expected Result:** Each request returns a 4xx error with a clear validation message identifying the missing field. No bet created, no balance change.

#### TC-17: Place-bet with invalid selection enum
- **Spec Ref:** 4.2
- **Priority:** Medium
- **Risk Rationale:** An unrecognized selection value that silently maps to a valid outcome could create a bet with odds the user did not choose.
- **Steps:** 1. Send `POST /api/place-bet` with `selection: "INVALID"`. 2. Repeat with `selection: ""`. 3. Repeat with `selection: "home"` (lowercase).
- **Expected Result:** All rejected with a 4xx error. No bet created.

#### TC-18: Place-bet with non-existent match ID
- **Spec Ref:** 4.2
- **Priority:** Medium
- **Risk Rationale:** If the server does not validate match existence before processing, it could create a bet record against a phantom match with undefined odds — a data integrity risk.
- **Steps:** Send `POST /api/place-bet` with `matchId: "does-not-exist-12345"`, a valid selection, and a valid stake.
- **Expected Result:** Rejected with a 4xx error (match not found). No bet created, no balance change.

#### TC-19: Place-bet response schema and payout calculation
- **Spec Ref:** 2.4 / 3
- **Priority:** Medium
- **Risk Rationale:** If the API response omits fields or returns incorrect payout, the UI (or any consumer) may display wrong information to the user.
- **Steps:** 1. Place a valid bet via API. 2. Validate the response contains all expected fields: `message`, `matchId`, `selection`, `stake`, `odds`, `payout`, `balance`, `currency`. 3. Verify `payout == stake × odds`. 4. Verify `balance == pre-bet balance − stake`.
- **Expected Result:** All fields present and correctly typed. Payout and balance calculations are exact (within rounding tolerance).

#### TC-20: HTTP method guarding on action endpoints
- **Spec Ref:** 5.1
- **Priority:** Medium
- **Risk Rationale:** Unguarded GET on an action endpoint exposes the system to CSRF-style attacks (cached links, crawlers) and indicates inconsistent API hardening.
- **Steps:** 1. Send `GET /api/place-bet` with valid headers. 2. Send `PUT /api/place-bet`. 3. Send `DELETE /api/place-bet`. 4. Repeat all for `/api/reset-balance`.
- **Expected Result:** All non-POST methods return 405 Method Not Allowed. No side effects (no bet placed, no balance reset).

#### TC-21: Odds filter uses inclusive boundaries
- **Spec Ref:** 2.9
- **Priority:** Medium
- **Risk Rationale:** An exclusive boundary (using `>` instead of `>=`) hides matches from users whose filter exactly matches available odds — a usability defect that may cost conversions.
- **Steps:** 1. Identify a match with a known home odd (e.g. 2.45). 2. Set the odds filter min to that exact value. 3. Observe whether the match remains in the list. 4. Set the odds filter max to that exact value with a low min. 5. Observe whether the match remains.
- **Expected Result:** Matches with odds exactly at the min or max boundary remain visible (inclusive: `>=` and `<=`).

#### TC-22: Date filter correctly filters matches by range
- **Spec Ref:** 2.8
- **Priority:** Medium
- **Risk Rationale:** An incorrect date filter could hide upcoming bettable matches or show irrelevant past matches, impacting user experience and revenue.
- **Steps:** 1. Note a match with a known kickoff date from the API. 2. Set the date filter to a range that includes that date — verify match is shown. 3. Set the date filter to a range that excludes that date — verify match is hidden.
- **Expected Result:** Only matches whose kickoff date falls within the selected range are displayed.

#### TC-23: Balance updates in UI after successful bet without refresh
- **Spec Ref:** 2.4
- **Priority:** Medium
- **Risk Rationale:** A stale balance display after a successful bet lets the user believe they have more funds than they do, leading to attempted over-betting and a poor experience. Also enables sequential over-betting before the UI catches up.
- **Steps:** 1. Reset balance. Record UI balance. 2. Place a valid bet. 3. Without refreshing the page, immediately read the UI header balance. 4. Compare to expected: pre-bet balance minus stake.
- **Expected Result:** UI balance updates immediately (or within a short, reasonable delay) to reflect the deduction, without requiring a manual page refresh.

#### TC-24: Bet slip selection removal returns to idle state
- **Spec Ref:** 2.2
- **Priority:** Medium
- **Risk Rationale:** If removing a selection leaves residual state (a stale stake, a phantom payout), the next bet flow may start from a corrupt state.
- **Steps:** 1. Select an outcome — bet slip populates. 2. Enter a stake. 3. Click "Remove All" or equivalent removal control. 4. Inspect the bet slip.
- **Expected Result:** Bet slip returns to idle: no selection displayed, stake input cleared, no payout shown, Place Bet button disabled or hidden.

#### TC-25: Match list displays correct data from API
- **Spec Ref:** 2.1
- **Priority:** Medium
- **Risk Rationale:** If the UI renders teams or odds incorrectly compared to the API source, the user may bet on the wrong outcome at wrong odds.
- **Steps:** 1. Fetch matches via `GET /api/matches`. 2. For at least one match, locate it in the UI. 3. Compare displayed home team, away team, competition, date, and all three odds values.
- **Expected Result:** UI display matches API data for all fields.

#### TC-26: Non-numeric and edge-case stake values rejected
- **Spec Ref:** 4.1
- **Priority:** Low
- **Risk Rationale:** Non-numeric stake input that passes validation could produce undefined server behavior or a zero-value bet.
- **Steps:** 1. Via API: send `place-bet` with `stake: "abc"`. 2. Repeat with `stake: null`. 3. Repeat with `stake: 0`. 4. Via UI: type "abc" into stake input, observe validation.
- **Expected Result:** All non-numeric and zero values rejected. No bet created, no balance change.

#### TC-27: Place-bet currency field consistency
- **Spec Ref:** 3
- **Priority:** Low
- **Risk Rationale:** A currency mismatch between API response and UI display is a compliance and correctness issue for any multi-currency or regulated environment.
- **Steps:** 1. Place a valid bet via API. 2. Check the `currency` field in the response. 3. Compare to the currency symbol shown in the UI header balance and bet slip.
- **Expected Result:** Currency in API response matches the currency displayed throughout the UI (both should be EUR/€ or both USD/$, consistently).

---

## 6. Test Automation, Tech Stack & Test Environment

**Tech stack**

| Layer | Tool |
|---|---|
| Language | Python 3 |
| UI automation | Selenium WebDriver + Pytest |
| API testing | Python `requests` library |

**Browser target:** Latest desktop Chrome only (per spec, mobile UX is out of scope).

**Test environment:** [https://qae-assignment-tau.vercel.app/](https://qae-assignment-tau.vercel.app/)

**Test user:** `candidate-LfzI2CKDRw` (used as the `user-id` header value where a single test user is sufficient).

**API documentation:** available at `/api/docs` (Swagger UI) on the environment above.

**Test data:** the environment's match data is a **snapshot of real production data from actual games**, not synthetic test fixtures. 

## 7. Item Pass/Fail Criteria

A test case **passes** when actual behavior, displayed values, persisted state, and API response match the Feature Specification exactly, including monetary values to the cent.

A test case **fails** if any of the following occur, regardless of whether the "main" assertion passed:
- Balance changes by an amount inconsistent with stake/payout
- A bet is placed without passing all applicable validation rules
- A duplicate bet is created from a single user action
- Stake, odds, or payout displayed to the user differs from what is persisted/returned by the API
- Error or loading states fail to resolve to exactly one final outcome

## 8. Entry Criteria
- Feature Specification is approved/baselined
- Test environment is deployed and reachable, with `/api/docs` available
- Test data available: at least one configured user with known starting balance, and seeded matches covering varied odds
- Reset-balance endpoint is functional (needed to reset state between test runs)

## 9. Exit Criteria
- 100% of business rules and validation rules have at least one executed test case
- All Critical/High severity defects are resolved or formally waived by product owner
- No open defect allows: negative balance, stake bypass, duplicate bet placement, or unauthorized access to another user's balance/bet

## 10. Suspension and Resumption Criteria
Testing is suspended if: the test environment cannot reliably reset balance/state between runs, or if a Critical defect (e.g. balance corruption, duplicate bet creation) blocks further reliable testing. Testing resumes once the blocking defect is fixed and verified in a clean environment.

## 11. Test Deliverables
- This test plan
- Automated test suite (Pytest, Selenium, requests) cross-referenced to the scenario IDs in Section 6
- Defect reports
- Test execution summary / closure report

## 12. Roles and Responsibilities

| Role | Responsibility |
|---|---|
| QA Engineer | Design and execute test cases, log defects, verify fixes |
| Developer | Fix defects, support root-cause analysis on money-related findings |
| Product Owner | Approve scope, sign off on exit criteria, waive/accept residual risk if any |

## 13. Use of AI Tools in Testing

Using AI tools as part of this effort is a good idea, but only within a defined scope — this is core money-moving functionality, so AI output is treated as a draft to be verified, not an authority.

**Recommended scope (AI-assisted, human-reviewed):**
- Drafting additional edge-case ideas from the spec (especially boundary and negative cases) for a human to triage into Section 6
- Generating Selenium/Pytest boilerplate and fixtures, refactoring repetitive test code
- Summarizing/triaging large test-run logs, flagging likely flaky vs. genuine failures
- Drafting documentation (test summaries, defect descriptions) for human review before publishing

**Out of scope / not permitted without explicit human sign-off:**
- AI must never be the sole determinant of a pass/fail verdict on a money-correctness assertion (stake, odds, payout, balance) — a human must verify these against the Business Rules table
- Do not feed the production data snapshot (Section 7) into external/third-party AI tools; if AI assistance needs example data, use synthetic/anonymized values instead, since the real snapshot originates from production
- AI must not be used to auto-generate and auto-execute destructive or state-changing calls (e.g. bulk `reset-balance` or `place-bet` calls) without a human reviewing the generated script first
- Security-critical test cases must be designed and reviewed by a human; AI may assist with drafting but not be the final author


## 14. Open Questions / Items to Clarify with the Team

The Feature Specification leaves several things undefined that affect test scope and should be discussed with the product owner/team before — or early in — test execution, rather than assumed unilaterally by QA.

Stake minimum inconsistency. The Feature Specification is internally inconsistent on the minimum stake value:

The Business Rules table states the stake minimum is €1.00
The Stake Validation table states the stake minimum is €1.01 (positive values)
The UI Error Messaging note states the displayed message is "Minimum stake is €1.00"


This must be clarified before boundary test cases are added, since €1.00 vs €1.01 changes the expected result for a boundary value test at exactly €1.00. Until clarified, both values will be tested and the actual implemented behavior flagged against whichever the business confirms as correct.
Supported browser/OS matrix. The spec only says "Desktop web application" and excludes mobile UX — it does not state which browsers, versions, or operating systems must be supported. This test plan automates against the latest desktop Chrome only as a practical default; the team should confirm whether other browsers (Firefox, Safari, Edge) or older versions need coverage, and whether that coverage should be automated or left to manual/exploratory spot-checks.
Time zone handling for kickoff times. The spec shows kickoffDate as a date-only string; it doesn't clarify the time component's time zone (user-local vs. fixed). Worth confirming so date-filter and kickoff-display tests assert the right thing.
Performance/load expectations. No non-functional targets (response time, concurrent users) are stated. Even a rough target would help size load/performance testing, particularly around place-bet under concurrency.
Session and multi-device behavior. Not addressed: what happens if the same user has the bet slip open in two tabs/devices simultaneously — relevant given odds are "static for session" and ties into the double-submit risk.