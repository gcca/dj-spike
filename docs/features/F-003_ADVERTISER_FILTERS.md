# F-003: Advertiser Filters

**Status:** Open
**Impact:** Enable filtering on the advertisers list endpoint via query parameters using django-filter — exact match, comparators (gte, lte, gt, lt), and datetime range for `created_at` and `updated_at`.

## Problem

The advertisers list endpoint (`GET /api/v1/advertisers/`) returns all advertisers without filtering. Users need to filter by:

- **Datetime range:** `created_at` and `updated_at` (e.g. advertisers created after a date, updated within a range)
- **Exact values:** `name`, `monetization_type`, `billing_source`, `billing_timezone`
- **Comparators:** `discount`, `default_conversion_rate` (e.g. discount >= 0.05, conversion rate < 0.02)

This supports auditing, reporting, and operational queries without fetching the full dataset.

## Solution

### Overview

- Use **django-filter** to add a `FilterSet` for the `Advertiser` model.
- Attach the `FilterSet` to `AdvertiserViewSet` via `filter_backends` and `filterset_class`.
- Expose filter parameters as query params on `GET /api/v1/advertisers/`.

### Filter Specification

| Field | Filter types | Query params | Example |
|-------|--------------|--------------|---------|
| `created_at` | Datetime range | `created_at_after`, `created_at_before` | `?created_at_after=2025-01-01T00:00:00Z` |
| `updated_at` | Datetime range | `updated_at_after`, `updated_at_before` | `?updated_at_before=2025-03-01T23:59:59Z` |
| `name` | Exact, contains | `name`, `name__icontains` | `?name=Acme`, `?name__icontains=corp` |
| `monetization_type` | Exact | `monetization_type` | `?monetization_type=CPC` |
| `billing_source` | Exact | `billing_source` | `?billing_source=INTERNAL` |
| `billing_timezone` | Exact | `billing_timezone` | `?billing_timezone=UTC` |
| `discount` | Exact, gte, lte, gt, lt | `discount`, `discount__gte`, `discount__lte`, etc. | `?discount__gte=0.05` |
| `default_conversion_rate` | Exact, gte, lte, gt, lt | `default_conversion_rate`, `default_conversion_rate__gte`, etc. | `?default_conversion_rate__lte=0.01` |

**Datetime format:** ISO 8601 (e.g. `2025-01-01T00:00:00Z` or `2025-01-01T00:00:00`). Timezone-aware values recommended.

**Invalid enum values:** Use `ChoiceFilter` with explicit `choices` (from `MonetizationType`, `BillingSource`, `BillingTimezone`). Invalid values return 400 with validation message.

### Dependencies

- **F-001:** Advertiser API must exist.
- **django-filter:** Already in `pyproject.toml`. Add `django_filters` to `INSTALLED_APPS` and configure `DjangoFilterBackend` for DRF.
- **F-002:** If F-002 is in progress, coordinate changes in `views.py` and `test_views.py` (both features modify them).

---

## Files to Create / Modify

| File | Action | Purpose |
|------|--------|---------|
| `dj_advertisers/filters.py` | CREATE | `AdvertiserFilterSet` with all filter definitions |
| `dj_spike/settings.py` | MODIFY | Add `django_filters` to `INSTALLED_APPS`; create `REST_FRAMEWORK` block if it does not exist with `DEFAULT_FILTER_BACKENDS: [DjangoFilterBackend]` |
| `dj_advertisers/tests/test_filters.py` | CREATE | FilterSet unit tests |
| `dj_advertisers/views.py` | MODIFY | Add `filter_backends`, `filterset_class` to `AdvertiserViewSet` |
| `dj_advertisers/tests/test_views.py` | MODIFY | Add API tests for filter query params |

---

## Two-Worker Task Distribution

Workers must not modify the same files. Execution order: **Worker A first**, then **Worker B** (B depends on A), then **Worker Test** (depends on A and B).

### Worker A — FilterSet, Settings, Filter Tests

| Task | Files | Instructions |
|------|-------|--------------|
| Create FilterSet | `dj_advertisers/filters.py` | Create `AdvertiserFilterSet` with `Meta.model = Advertiser`. Use `IsoDateTimeFromToRangeFilter` for `created_at` and `updated_at` (params `*_after`, `*_before`, ISO 8601). Declare explicitly: `name` and `name__icontains` (CharFilter); `discount`, `discount__gte`, `discount__lte`, etc. (NumberFilter); enums with `ChoiceFilter` and model `choices` |
| Update settings | `dj_spike/settings.py` | Add `django_filters` to `INSTALLED_APPS`. Create `REST_FRAMEWORK` block if it does not exist; add `DEFAULT_FILTER_BACKENDS: ["django_filters.rest_framework.DjangoFilterBackend"]` |
| Create filter tests | `dj_advertisers/tests/test_filters.py` | Test FilterSet: filter by created_at range, updated_at range, exact name, monetization_type, discount comparators, etc. |

**Worker A must not touch:** `dj_advertisers/views.py`, `dj_advertisers/tests/test_views.py`

**Pre-commit:** Run only on modified files: `pre-commit run --files dj_advertisers/filters.py dj_spike/settings.py dj_advertisers/tests/test_filters.py`

### Worker B — View Integration, API Tests

| Task | Files | Instructions |
|------|-------|--------------|
| Wire FilterSet to ViewSet | `dj_advertisers/views.py` | Add `filter_backends = [DjangoFilterBackend]` and `filterset_class = AdvertiserFilterSet` to `AdvertiserViewSet` |
| Add filter API tests | `dj_advertisers/tests/test_views.py` | Test `GET /api/v1/advertisers/?param=value` for each filter type: created_at range, updated_at range, name, monetization_type, discount__gte, etc. Verify filtered results. |

**Worker B must not touch:** `dj_advertisers/filters.py`, `dj_spike/settings.py`, `dj_advertisers/tests/test_filters.py`

**Pre-commit:** Run only on modified files: `pre-commit run --files dj_advertisers/views.py dj_advertisers/tests/test_views.py`

### Worker Test — Unit Test Execution and E2E (Httpie)

Worker Test does **not** create or modify files. It runs unit tests and e2e checks.

| Task | Instructions |
|------|--------------|
| Run unit tests | `python manage.py test dj_advertisers` — all tests must pass |
| Launch test server | `python manage.py runserver` (or `gunicorn dj_spike.wsgi:application`) — keep running in background |
| Run e2e (Httpie) | Execute the Httpie commands below. Verify status 200 and that filters narrow results. |

**E2E cases (mirror unit tests):**

1. **List with created_at range** — `http GET ":8000/api/v1/advertisers/?created_at_after=2025-01-01T00:00:00Z"` → 200, filtered list
2. **List with updated_at range** — `http GET ":8000/api/v1/advertisers/?updated_at_before=2025-03-01T23:59:59Z"` → 200
3. **List with exact monetization_type** — `http GET ":8000/api/v1/advertisers/?monetization_type=CPC"` → 200
4. **List with discount comparator** — `http GET ":8000/api/v1/advertisers/?discount__gte=0.05"` → 200
5. **List with name search** — `http GET ":8000/api/v1/advertisers/?name__icontains=Acme"` → 200

**Worker Test must not touch:** any source or test files (read-only execution).

---

## Agent Implementation Checklist

1. **Worker A**
   - Create `dj_advertisers/filters.py` with `AdvertiserFilterSet`.
   - For `created_at` and `updated_at`: use `IsoDateTimeFromToRangeFilter` (params `created_at_after`, `created_at_before`; accepts ISO 8601).
   - For `name`: declare both filters: `name = CharFilter(field_name='name', lookup_expr='exact')` and `name__icontains = CharFilter(field_name='name', lookup_expr='icontains')`.
   - For `monetization_type`, `billing_source`, `billing_timezone`: `ChoiceFilter` with model `choices` (invalid values → 400).
   - For `discount`, `default_conversion_rate`: declare each lookup explicitly: `discount__gte = NumberFilter(field_name='discount', lookup_expr='gte')`, etc.
   - Add `django_filters` to `INSTALLED_APPS`. Create `REST_FRAMEWORK = {"DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.DjangoFilterBackend"]}` if it does not exist in settings.
   - Create `dj_advertisers/tests/test_filters.py` — test FilterSet in isolation.
   - Run `python manage.py test dj_advertisers.tests.test_filters`.
   - Run `pre-commit run --files dj_advertisers/filters.py dj_spike/settings.py dj_advertisers/tests/test_filters.py` after changes.

2. **Worker B**
   - Add `filter_backends = [DjangoFilterBackend]` and `filterset_class = AdvertiserFilterSet` to `AdvertiserViewSet`.
   - Add filter API tests in `dj_advertisers/tests/test_views.py`.
   - Run `python manage.py test dj_advertisers`.
   - Run `pre-commit run --files dj_advertisers/views.py dj_advertisers/tests/test_views.py` after changes.

3. **Worker Test**
   - Run `python manage.py test dj_advertisers` — all unit tests must pass.
   - Launch server and execute Httpie examples below. Verify filters affect results.

---

## Httpie Examples (Manual / E2E)

Use `http` (httpie) against `localhost:8000`. Document each endpoint with the exact command and expected outcome. Server must be running.

```bash
# List all — 200, full list
http GET ":8000/api/v1/advertisers/"

# Filter by created_at (after) — 200, advertisers created after given datetime
http GET ":8000/api/v1/advertisers/?created_at_after=2025-01-01T00:00:00Z"

# Filter by created_at range — 200, advertisers created within range
http GET ":8000/api/v1/advertisers/?created_at_after=2025-01-01T00:00:00Z&created_at_before=2025-03-01T23:59:59Z"

# Filter by updated_at (before) — 200, advertisers updated before given datetime
http GET ":8000/api/v1/advertisers/?updated_at_before=2025-03-01T23:59:59Z"

# Filter by monetization_type — 200, only CPC advertisers
http GET ":8000/api/v1/advertisers/?monetization_type=CPC"

# Filter by billing_source — 200, only INTERNAL
http GET ":8000/api/v1/advertisers/?billing_source=INTERNAL"

# Filter by discount >= 0.05 — 200, advertisers with discount >= 5%
http GET ":8000/api/v1/advertisers/?discount__gte=0.05"

# Filter by name contains — 200, advertisers whose name contains "Acme"
http GET ":8000/api/v1/advertisers/?name__icontains=Acme"

# Combined filters — 200, CPC advertisers with discount >= 0.05
http GET ":8000/api/v1/advertisers/?monetization_type=CPC&discount__gte=0.05"
```

**Expected response example (200 OK, filtered by monetization_type=CPC):**

```json
[
  {
    "id": 1,
    "name": "Acme Corp",
    "discount": "0.0500",
    "default_conversion_rate": "0.0100",
    "monetization_type": "CPC",
    "billing_source": "INTERNAL",
    "billing_timezone": "UTC",
    "created_at": "2025-02-15T10:00:00Z",
    "updated_at": "2025-03-01T14:30:00Z"
  }
]
```

---

## Verification

1. `python manage.py test dj_advertisers` — all unit tests pass.
2. Run Httpie examples above against a running server with sample data.
3. Verify datetime range filters work with ISO 8601 format.
4. `pre-commit run --files <modified files>` — passes per worker.

---

## Related

- F-001: Advertiser API (required)
- F-002: Advertiser Performance Report — coordinate if both in progress (share `views.py`, `test_views.py`)
- Tech stack: `AGENTS.md`
- django-filter: see `pyproject.toml`; `IsoDateTimeFromToRangeFilter` for ISO 8601
