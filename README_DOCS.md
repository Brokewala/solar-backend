# Endpoint Export

Generate shareable documentation of all API endpoints.

## Usage

```bash
python manage.py export_endpoints --format md,json --out docs/ENDPOINTS.md --openapi docs/openapi.json --base-url https://api.example.com
```

The command writes:

- `docs/ENDPOINTS.md` – human-friendly overview grouped by app.
- `docs/openapi.json` – OpenAPI 3 schema.

Share these two files with anyone who needs to explore the API.
