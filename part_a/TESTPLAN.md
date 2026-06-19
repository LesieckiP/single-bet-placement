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

#### TC-02: Successful placement deducts stake exactly once
- **Spec Ref:** 2.3 / 2.4
- **Priority:** Critical
- **Risk Rationale:** Core money-correctness assertion — incorrect or duplicate deduction is a direct financial leak.
- **Steps:** 1. Record balance. 2. Place a valid bet of known stake. 3. Re-check balance via UI and `GET /api/balance`.
- **Expected Result:** Balance decreases by exactly the stake amount, once, and matches across UI and API.

#### TC-03: Stake exceeding balance
- **Spec Ref:** 3 / 4.1
- **Priority:** Critical
- **Risk Rationale:** Allowing a bet beyond available balance is a direct path to a negative balance / money leak.
- **Steps:** 1. Note current balance. 2. Attempt a stake greater than balance via UI. 3. Repeat via direct API call.
- **Expected Result:** Rejected at both layers with "Insufficient balance" messaging; balance is unchanged.

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