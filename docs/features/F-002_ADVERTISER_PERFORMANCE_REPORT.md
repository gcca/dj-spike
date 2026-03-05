# F-002: Advertiser Performance Report

**Status:** Open
**Impact:** Consolidated performance report per advertiser for account management, sales, operations, finance, and leadership — with normalized metrics, billing timezone support, and flexible filters.

## Problem

Internal teams (account management, sales, operations, finance, leadership) need to quickly and reliably consult the commercial and financial performance of each advertiser over a given period. The report must show:

- Normalized, consistent metrics reflecting real billed spend (after discounts) and results
- Correct handling of billing timezones (UTC, EST, CST, PST) when aggregating by day
- Support for both CPC and CPA monetization models
- Filters and sorting to prioritize advertisers, compare models, and support resource allocation, renegotiation, or corrective actions

**Typical use contexts:**
- Weekly or monthly advertiser portfolio review
- Preparation for commercial or results review meetings
- Identification of priority or at-risk advertisers
- Comparison between CPC and CPA models
- Support for resource allocation, renegotiation, or corrective decisions

## Solution

### Overview

- Expose a **report API** at `{host}/api/v1/advertisers/performance-report/` (or similar).
- Accept **date range** (required) and optional filters: monetization model, billing source, timezone, advertiser name search.
- Support **sorting** by effective spend, conversions, CTR, effective CPA, effective CPC, name.
- Return per-advertiser metrics: identification, volume (impressions, clicks, conversions, CTR), and economics (gross spend, discount, net spend, effective CPC/CPA).
- Respect **billing timezone** when determining which events belong to each day.
- Handle edge cases: no activity, model changes mid-period, zero divisions, wide date ranges.

### Report Data per Advertiser

| Category | Field | Description |
|----------|-------|-------------|
| **Identification** | `id` | Advertiser ID |
| | `name` | Commercial name |
| | `monetization_type` | CPC or CPA |
| | `billing_source` | Internal or Partner |
| **Volume** | `impressions` | Total impressions |
| | `clicks` | Total clicks |
| | `conversions` | Total conversions |
| | `ctr` | Clicks / impressions (percentage) |
| **Economics** | `gross_spend` | Amount before discount |
| | `discount_rate` | Applied discount (percentage or absolute) |
| | `discount_amount` | Discount applied |
| | `net_spend` | Real billed amount (gross − discount) |
| | `effective_cpc` | Shown only if clicks and/or CPC model |
| | `effective_cpa` | Shown only if conversions and/or CPA model |

### Query Parameters

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `date_from` | Yes | — | Start of period (inclusive) |
| `date_to` | Yes | — | End of period (inclusive) |
| `monetization_type` | No | all | CPC, CPA, or all |
| `billing_source` | No | all | Internal, Partner, or all |
| `billing_timezone` | No | all | UTC, EST, CST, PST, or all |
| `search` | No | — | Partial advertiser name search |
| `order_by` | No | `net_spend` | `net_spend`, `conversions`, `ctr`, `effective_cpa`, `effective_cpc`, `name` |
| `order` | No | `desc` | `asc` or `desc` |

### Business Rules

- **Timezone:** For each advertiser, use its billing timezone to determine which events fall into each day of the selected range.
- **Historical consistency:** If an advertiser changed discount, monetization, or timezone during the period, use the value that applied on each day.
- **Division by zero:** Handle CTR, effective CPC, effective CPA safely (e.g., null or 0).
- **No activity:** Advertisers with no activity may be omitted or shown with zeros (product decision).
- **Currency:** Monetary values with 2 decimals, in platform base currency.
- **Performance:** Report should load quickly even with hundreds or thousands of active advertisers.

### Edge Cases

- Advertiser with no activity in the period
- Advertiser that switched from CPC to CPA during the period
- Advertiser with 0% vs very high discount (>30–40%)
- Very wide date range (6–12 months)
- Advertiser timezone different from user’s
- Zero impressions but conversions present (possible fraud/error — must be visible)

### Dependencies

- **F-001:** Advertiser model and API must exist (advertiser id, name, monetization_type, billing_source, billing_timezone, discount).
- **Data source:** This feature assumes a source of events (impressions, clicks, conversions, spend). The exact schema and storage are out of scope for this F; the report API should be designed to consume aggregated or raw data from a service or table to be defined.

---

## Files to Create / Modify

| File | Action | Purpose |
|------|--------|---------|
| `dj_advertisers/serializers.py` | MODIFY | Add `PerformanceReportRowSerializer` for report response |
| `dj_advertisers/services.py` | CREATE | Report aggregation logic (filters, sorting, timezone, metrics) |
| `dj_advertisers/tests/test_report.py` | CREATE | Report service and serializer unit tests |
| `dj_advertisers/views.py` | MODIFY | Add report action or view that calls service |
| `dj_advertisers/urls.py` | MODIFY | Wire report endpoint |
| `dj_advertisers/tests/test_views.py` | MODIFY | Add report API tests |

---

## Two-Worker Task Distribution

Workers must not modify the same files. Execution order: **Worker A first**, then **Worker B** (B depends on A), then **Worker Test** (depends on A and B).

### Worker A — Report Serializer, Service, Service Tests

| Task | Files | Instructions |
|------|-------|--------------|
| Add report serializer | `dj_advertisers/serializers.py` | Add `PerformanceReportRowSerializer` with fields: id, name, monetization_type, billing_source, impressions, clicks, conversions, ctr, gross_spend, discount_rate, discount_amount, net_spend, effective_cpc, effective_cpa |
| Create report service | `dj_advertisers/services.py` | Implement `get_performance_report(date_from, date_to, filters)` — aggregation logic, filters (monetization_type, billing_source, billing_timezone, search), sorting. Use Advertiser model; event data can be stubbed until schema exists |
| Create report tests | `dj_advertisers/tests/test_report.py` | Test serializer output; test service filters, sorting, division-by-zero, empty results |

**Worker A must not touch:** `dj_advertisers/views.py`, `dj_advertisers/urls.py`, `dj_advertisers/tests/test_views.py`

**Pre-commit:** Run only on modified files: `pre-commit run --files dj_advertisers/serializers.py dj_advertisers/services.py dj_advertisers/tests/test_report.py`

### Worker B — Report View, URL Wiring, API Tests

| Task | Files | Instructions |
|------|-------|--------------|
| Add report view | `dj_advertisers/views.py` | Add report action to `AdvertiserViewSet` or dedicated view; parse query params (date_from, date_to, monetization_type, billing_source, billing_timezone, search, order_by, order); call service; return serialized data |
| Wire report URL | `dj_advertisers/urls.py` | Register report endpoint (e.g. `advertisers/performance-report/`) |
| Add report API tests | `dj_advertisers/tests/test_views.py` | Test report endpoint: required params, filters, sorting, status codes |

**Worker B must not touch:** `dj_advertisers/serializers.py`, `dj_advertisers/services.py`, `dj_advertisers/tests/test_report.py`

**Pre-commit:** Run only on modified files: `pre-commit run --files dj_advertisers/views.py dj_advertisers/urls.py dj_advertisers/tests/test_views.py`

### Worker Test — Unit Test Execution and E2E (Httpie)

Worker Test does **not** create or modify files. It runs unit tests and e2e checks.

| Task | Instructions |
|------|--------------|
| Run unit tests | `python manage.py test dj_advertisers` — all tests must pass |
| Launch test server | `python manage.py runserver` (or `gunicorn dj_spike.wsgi:application`) — keep running in background |
| Run e2e (Httpie) | Execute the Httpie commands below. Verify status 200, response structure, and that filters/sorting affect results. |

**E2E cases (mirror unit tests):**

1. **Report with date range** — `http GET ":8000/api/v1/advertisers/performance-report/?date_from=2025-02-01&date_to=2025-03-01"` → 200, list of report rows
2. **Report with filters** — `http GET ":8000/api/v1/advertisers/performance-report/?date_from=2025-02-01&date_to=2025-03-01&monetization_type=CPC"` → 200
3. **Report with sorting** — `http GET ":8000/api/v1/advertisers/performance-report/?date_from=2025-02-01&date_to=2025-03-01&order_by=conversions&order=desc"` → 200
4. **Report with search** — `http GET ":8000/api/v1/advertisers/performance-report/?date_from=2025-02-01&date_to=2025-03-01&search=Acme"` → 200

**Worker Test must not touch:** any source or test files (read-only execution).

---

## Agent Implementation Checklist

1. **Worker A**
   - Add `PerformanceReportRowSerializer` to `dj_advertisers/serializers.py` with all report fields.
   - Create `dj_advertisers/services.py` with `get_performance_report(date_from, date_to, **filters)`.
   - Implement filters: monetization_type, billing_source, billing_timezone, search.
   - Implement sorting: net_spend, conversions, ctr, effective_cpa, effective_cpc, name (asc/desc).
   - Handle division by zero for CTR, effective_cpc, effective_cpa.
   - Use Advertiser model; stub event data (impressions, clicks, conversions, spend) until schema exists.
   - Create `dj_advertisers/tests/test_report.py` — serializer and service tests.
   - Run `python manage.py test dj_advertisers.tests.test_report`.
   - Run `pre-commit run --files dj_advertisers/serializers.py dj_advertisers/services.py dj_advertisers/tests/test_report.py` after changes.

2. **Worker B**
   - Add report action or view in `dj_advertisers/views.py`; parse query params; call `get_performance_report`; return serialized response.
   - Wire report endpoint in `dj_advertisers/urls.py`.
   - Add report API tests in `dj_advertisers/tests/test_views.py`.
   - Run `python manage.py test dj_advertisers`.
   - Run `pre-commit run --files dj_advertisers/views.py dj_advertisers/urls.py dj_advertisers/tests/test_views.py` after changes.

3. **Worker Test**
   - Run `python manage.py test dj_advertisers` — all unit tests must pass.
   - Launch server: `python manage.py runserver` (or `gunicorn dj_spike.wsgi:application`).
   - Execute Httpie examples (see below). Verify status 200 and response structure.

---

## Httpie Examples (Manual / E2E)

Use `http` (httpie) against `localhost:8000`. Document each endpoint with the exact command and expected outcome. Server must be running (`python manage.py runserver` or `gunicorn dj_spike.wsgi:application`).

```bash
# Report for date range — 200, list of report rows (or empty [])
http GET ":8000/api/v1/advertisers/performance-report/?date_from=2025-02-01&date_to=2025-03-01"

# With filters: CPC only, Internal billing — 200, filtered list
http GET ":8000/api/v1/advertisers/performance-report/?date_from=2025-02-01&date_to=2025-03-01&monetization_type=CPC&billing_source=Internal"

# Sorted by conversions descending — 200, list ordered by conversions
http GET ":8000/api/v1/advertisers/performance-report/?date_from=2025-02-01&date_to=2025-03-01&order_by=conversions&order=desc"

# Search by advertiser name — 200, list matching search
http GET ":8000/api/v1/advertisers/performance-report/?date_from=2025-02-01&date_to=2025-03-01&search=Acme"

# Sorted by effective CPA ascending (most expensive first) — 200, list ordered by effective_cpa asc
http GET ":8000/api/v1/advertisers/performance-report/?date_from=2025-02-01&date_to=2025-03-01&order_by=effective_cpa&order=asc"
```

---

## Verification

1. `python manage.py test dj_advertisers` — all unit tests pass.
2. Run Httpie examples above against a running server with sample data.
3. Verify edge cases: no activity, zero divisions, timezone boundaries.
4. `pre-commit run --files <modified files>` — passes per worker.

---

## Related

- F-001: Advertiser API (required)
- Tech stack: `AGENTS.md`
