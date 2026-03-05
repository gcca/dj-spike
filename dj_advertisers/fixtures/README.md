# Fixtures

Sample data for manual and e2e testing.

## advertiser.yaml

Load before manual or e2e tests:

```bash
python manage.py loaddata advertiser
```

Provides 3 advertisers: Acme Corp (CPC), Beta Partners Inc (CPA, PARTNER), Gamma Jobs (CPC). `billing_source` values must match the PostgreSQL enum in your database (e.g. JOBLEAP or INTERNAL).
