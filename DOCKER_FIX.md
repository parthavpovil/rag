# Quick Fix Guide for Docker Import Error

## Problem
Container was crashing with:
```
ImportError: attempted relative import beyond top-level package
```

## Root Cause
Mixed import styles:
- `main.py` used absolute imports: `from api.routes import router`
- `routes.py` used relative imports: `from ..services import ...`

## Solution
Changed all imports to absolute style:

**main.py:**
```python
from api.routes import router  # ✅ Absolute
```

**routes.py:**
```python
from services import vectordb, ...  # ✅ Absolute
from api.models import ...  # ✅ Absolute
```

## How to Apply on Server

```bash
cd ~/opt/rag
git pull  # Get latest changes
docker compose down
docker compose build rag-service
docker compose up -d rag-service
docker logs -f rag-service  # Should see "Application startup complete"
```

## Verify It Works
```bash
curl http://localhost:8000/health
# Should return: {"status":"ok"}
```
