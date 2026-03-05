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
| | `billing_source` | `INTERNAL` o `PARTNER` (valores enum) |
| **Volume** | `impressions` | Total impressions |
| | `clicks` | Total clicks |
| | `conversions` | Total conversions |
| | `ctr` | Clicks / impressions (percentage) |
| **Economics** | `gross_spend` | Amount before discount |
| | `discount_rate` | Applied discount (percentage or absolute) |
| | `discount_amount` | Discount applied |
| | `net_spend` | Real billed amount (gross − discount) |
| | | `effective_cpc` | `net_spend / clicks`; omitido si `clicks == 0` o modelo CPA; si no aplica, enviar `null` |
| | `effective_cpa` | `net_spend / conversions`; omitido si `conversions == 0` o modelo CPC; si no aplica, enviar `null` |

### Query Parameters

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `date_from` | Yes | — | Start of period (inclusive). Formato `YYYY-MM-DD`, interpretado en UTC |
| `date_to` | Yes | — | End of period (inclusive). Formato `YYYY-MM-DD`, interpretado en UTC |
| `monetization_type` | No | all | `CPC`, `CPA`, o `all` |
| `billing_source` | No | all | `INTERNAL`, `PARTNER`, o `all` (valores del enum Advertiser) |
| `billing_timezone` | No | all | `UTC`, `EST`, `CST`, `PST`, o `all` |
| `search` | No | — | Partial advertiser name search |
| `order_by` | No | `net_spend` | `net_spend`, `conversions`, `ctr`, `effective_cpa`, `effective_cpc`, `name` |
| `order` | No | `desc` | `asc` or `desc` |

### Business Rules

- **Timezone:** For each advertiser, use its billing timezone to determine which events fall into each day of the selected range.
- **Historical consistency:** En esta iteración, el modelo Advertiser no tiene historial. Usar siempre los valores actuales del advertiser (discount, monetization_type, billing_timezone). La regla de "valor que aplicaba cada día" queda diferida a una feature futura con audit/historial.
- **Division by zero:** CTR con 0 impressions → `null`; effective_cpc con 0 clicks → `null`; effective_cpa con 0 conversions → `null`.
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

### Event Data Stub (for development and tests)

Until the event schema exists, the service must consume data from a stub. The stub should return aggregates per advertiser and date with at least:

| Field | Type | Description |
|-------|------|-------------|
| `advertiser_id` | int | FK to Advertiser |
| `date` | date | Day (YYYY-MM-DD) in advertiser's billing timezone |
| `impressions` | int | Total impressions |
| `clicks` | int | Total clicks |
| `conversions` | int | Total conversions |
| `gross_spend` | Decimal | Amount before discount |

The stub may return empty data or synthetic rows for testing filters, sorting, and division-by-zero. The service computes `ctr`, `discount_amount`, `net_spend`, `effective_cpc`, `effective_cpa` from these fields and the Advertiser's `discount`.

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
| Add report serializer | `dj_advertisers/serializers.py` | Add `PerformanceReportRowSerializer` con campos: id, name, monetization_type, billing_source (valores enum: INTERNAL, PARTNER), impressions, clicks, conversions, ctr, gross_spend, discount_rate, discount_amount, net_spend, effective_cpc, effective_cpa (null cuando no aplica) |
| Create report service | `dj_advertisers/services.py` | Implement `get_performance_report(date_from, date_to, filters)` — aggregation logic, filters (monetization_type, billing_source, billing_timezone, search), sorting. Use Advertiser model; consumir datos del stub según estructura definida en sección "Event Data Stub" |
| Create report tests | `dj_advertisers/tests/test_report.py` | Test serializer output; test service filters, sorting, division-by-zero, empty results |

**Worker A must not touch:** `dj_advertisers/views.py`, `dj_advertisers/urls.py`, `dj_advertisers/tests/test_views.py`

**Pre-commit:** Run only on modified files: `pre-commit run --files dj_advertisers/serializers.py dj_advertisers/services.py dj_advertisers/tests/test_report.py`

### Worker B — Report View, URL Wiring, API Tests

| Task | Files | Instructions |
|------|-------|--------------|
| Add report view | `dj_advertisers/views.py` | Añadir `@action(detail=False, url_path='performance-report')` al `AdvertiserViewSet`; parsear query params (date_from, date_to, monetization_type, billing_source, billing_timezone, search, order_by, order); llamar al service; devolver datos serializados |
| Wire report URL | `dj_advertisers/urls.py` | El `DefaultRouter` expone automáticamente la acción en `advertisers/performance-report/`; no requiere cambios si se usa `@action` en el ViewSet |
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
   - Use Advertiser model; consumir stub con estructura `advertiser_id`, `date`, `impressions`, `clicks`, `conversions`, `gross_spend` (ver sección Event Data Stub).
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

# With filters: CPC only, Internal billing — 200, filtered list (usar valores enum: INTERNAL, PARTNER)
http GET ":8000/api/v1/advertisers/performance-report/?date_from=2025-02-01&date_to=2025-03-01&monetization_type=CPC&billing_source=INTERNAL"

# Sorted by conversions descending — 200, list ordered by conversions
http GET ":8000/api/v1/advertisers/performance-report/?date_from=2025-02-01&date_to=2025-03-01&order_by=conversions&order=desc"

# Search by advertiser name — 200, list matching search
http GET ":8000/api/v1/advertisers/performance-report/?date_from=2025-02-01&date_to=2025-03-01&search=Acme"

# Sorted by effective CPA ascending (most expensive first) — 200, list ordered by effective_cpa asc
http GET ":8000/api/v1/advertisers/performance-report/?date_from=2025-02-01&date_to=2025-03-01&order_by=effective_cpa&order=asc"
```

**Ejemplo de respuesta esperada (200 OK):**

```json
[
  {
    "id": 1,
    "name": "Acme Corp",
    "monetization_type": "CPC",
    "billing_source": "INTERNAL",
    "impressions": 10000,
    "clicks": 250,
    "conversions": 12,
    "ctr": 2.5,
    "gross_spend": "500.00",
    "discount_rate": "0.0500",
    "discount_amount": "25.00",
    "net_spend": "475.00",
    "effective_cpc": "1.90",
    "effective_cpa": null
  }
]
```

Campos `effective_cpc` y `effective_cpa` son `null` cuando no aplican (p. ej. CPC sin clicks, CPA sin conversions).

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
