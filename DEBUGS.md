# Debug log

A running log of bugs hit while building this project, written so a
beginner can follow *what broke*, *why*, and *how we knew*. Newest entries
go at the bottom.

---

## Debug 001 — Streamlit couldn't reach the backend

**Symptom:** The app loaded fine at `http://localhost:8501/`, but clicking
**Send** crashed the page with a traceback ending in:

```
ConnectionRefusedError: [Errno 111] Connection refused
...
requests.exceptions.ConnectionError: HTTPConnectionPool(host='127.0.0.1', port=8000):
Max retries exceeded with url: /rag/query
```

### Root cause: "localhost" means something different inside a container

Each Docker container is its own tiny computer with its own `127.0.0.1`
("localhost"). When code running *inside the frontend container* asks for
`127.0.0.1:8000`, it's asking "is anything listening on port 8000 **on
me**?" — and the frontend container isn't running anything on port 8000.
The backend is a *different* container; from inside the frontend, it is
never reachable at `127.0.0.1`.

```
Your PC
├── frontend container   (127.0.0.1 here = frontend only)
│     requests.post("http://127.0.0.1:8000/...")  ❌ nothing here
│
└── backend container    (127.0.0.1 here = backend only)
      uvicorn listening on :8000                   ✅ but on a different machine
```

Docker Compose solves this by giving every container a hostname equal to
its service name, on a shared network. From the frontend container, the
backend is reachable at `http://backend:8000` — **not** `127.0.0.1:8000`.
`docker-compose.yaml` already knew this and passed it in:

```yaml
frontend:
  environment:
    - API_URL=http://backend:8000   # correct address, from inside Docker
```

The bug: [`frontend/src/frontend/app.py`](frontend/src/frontend/app.py)
never read that `API_URL` variable — it had the wrong address
hardcoded instead.

### The fix

```diff
+ import os
  import streamlit as st
  import requests
  from pathlib import Path

+ API_URL = os.environ.get("API_URL", "http://127.0.0.1:8000")
+
  ...
      response = requests.post(
-         "http://127.0.0.1:8000/rag/query", json={"prompt": text_input}
+         f"{API_URL}/rag/query", json={"prompt": text_input}
      )
```

`os.environ.get("API_URL", "http://127.0.0.1:8000")` reads the `API_URL`
environment variable if it's set (inside Docker, Compose sets it to
`http://backend:8000`), and falls back to `127.0.0.1:8000` if it isn't
(e.g. running `streamlit run app.py` directly on your own machine, with no
Docker involved).

| Where you run it | `API_URL` env var set? | Address actually used |
|---|---|---|
| `docker compose up` | Yes → `http://backend:8000` | `http://backend:8000` |
| `uv run streamlit run app.py` on your PC | No | `http://127.0.0.1:8000` (fallback) |

### How we confirmed it

Docker Compose logs show each container's own `print`/traceback output,
prefixed with the service name — that's how the `ConnectionRefusedError`
above was found:

```bash
docker compose logs frontend --tail=100
```

### Verifying the fix

After editing code that runs inside a container, you must rebuild the
image — just saving the file isn't enough, since the old code is already
baked into the running container:

```bash
docker compose up -d --build frontend
```

Then reload `http://localhost:8501/` and send a question again.
