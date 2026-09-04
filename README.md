# Black Swan AI War Room

A hackathon-ready full-stack scaffold for a dynamic multi-agent decision-intelligence platform.

## Stack
- Frontend: React + Vite + TypeScript
- Backend: FastAPI + SQLite
- AI runtime: Neuro SAN + Ollama (`llama3.1:8b` recommended)
- Quant tools: deterministic Python
- Security: request-size limits, CORS allowlist, security headers, URL allow/deny controls, validation, audit trails, no autonomous high-impact actions

## Important
This is a runnable development scaffold, not a production-certified or penetration-tested system. It provides decision support only. Validate all assumptions, sources, and outputs before consequential use.

## Quick start on Windows

### 1. Install prerequisites
- Python 3.11+
- Node.js 20+
- `uv`
- Ollama

```powershell
winget install Ollama.Ollama
ollama pull llama3.1:8b
```

### 2. Backend
```powershell
cd backend
copy .env.example .env
uv venv
uv pip install -r requirements.txt
uv run uvicorn app.main:app --reload --port 8000
```

### 3. Frontend
```powershell
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`.

### 4. Neuro SAN
Copy the following into an existing project created by `ns init`:
- `neuro-san/registries/black_swan_war_room.hocon`
- `neuro-san/coded_tools/black_swan_war_room/`

Merge `neuro-san/registries/manifest_patch.hocon` into the generated manifest by following the syntax of an existing manifest entry.

```powershell
$env:AGENT_TOOL_PATH='.\coded_tools'
$env:AGENT_MANIFEST_FILE='.\registries\manifest.hocon'
uv run ns check-config
uv run ns run
```

## Demo flow
1. Submit a business/investment decision.
2. Backend creates a case and asks for critical assumptions.
3. Run deterministic finance and scenario tools.
4. Map dependencies.
5. Generate a compound Black Swan scenario.
6. Contrarian challenges the consensus.
7. Evidence verifier fails closed on unsupported claims.
8. Committee produces a conditional recommendation requiring human approval.

## Security design
- No secrets in source code.
- Local/private network URLs are blocked by the evidence fetcher.
- Redirect destination is revalidated.
- Request bodies are size-limited.
- All API inputs use Pydantic validation.
- SQLite statements use SQLAlchemy parameterization.
- High-impact actions are draft-only.
- Audit events exclude raw secrets.
- CORS is restricted to configured origins.
- Security headers are attached to responses.

## Project status
Included and locally syntax-checked:
- FastAPI API
- SQLite persistence
- React dashboard source
- deterministic finance/scenario/dependency engines
- audit log APIs
- Neuro SAN network and coded tools
- backend tests

Not automatically validated in this sandbox:
- your Ollama installation and model performance
- your installed Neuro SAN manifest format
- npm package installation
- corporate/personal firewall behavior
- production security certification
