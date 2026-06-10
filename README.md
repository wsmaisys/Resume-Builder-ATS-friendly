# AI Resume Builder

A local FastAPI app that creates a tailored resume PDF and cover letter PDF from a pasted job description. It uses a cached master candidate profile, optional portfolio/GitHub enrichment, Mistral for structured reasoning, an ATS evaluation loop, and HTML/CSS PDF templates rendered with WeasyPrint.

## Run Locally

```powershell
python -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000`.

## Environment

The app accepts either variable name:

```env
MISTRAL_API_KEY=...
mistral_api_key=...
```

Optional:

```env
MISTRAL_MODEL=mistral-large-latest
GITHUB_TOKEN=...
```

PDF rendering uses WeasyPrint first, as planned. On Windows machines without GTK/Pango libraries, the app automatically falls back to ReportLab so generation still works locally.

## GitHub Token

Create a fine-grained personal access token for safer read-only enrichment:

1. Open GitHub settings.
2. Go to `Developer settings` -> `Personal access tokens` -> `Fine-grained tokens`.
3. Click `Generate new token`.
4. Name it something like `resume-builder-local`.
5. Set an expiration, for example 30 or 90 days.
6. Set the resource owner to your GitHub account.
7. Set repository access to either public repositories or selected repositories.
8. Grant read-only `Contents` permission. GitHub automatically includes metadata access.
9. Generate the token and paste it into `.env`:

```env
GITHUB_TOKEN=github_pat_...
```

The app only needs read access for profile enrichment, repo metadata, README excerpts, and recent commits.

## MCP Servers

This project includes two local MCP stdio servers that expose the enrichment tools:

```powershell
python -m app.mcp_servers.github_mcp
python -m app.mcp_servers.portfolio_mcp
```

Example MCP client config:

```json
{
  "mcpServers": {
    "resume-builder-github": {
      "command": "python",
      "args": ["-m", "app.mcp_servers.github_mcp"],
      "cwd": "C:\\Yegawasim\\GitHub\\Resume-Builder-app"
    },
    "resume-builder-portfolio": {
      "command": "python",
      "args": ["-m", "app.mcp_servers.portfolio_mcp"],
      "cwd": "C:\\Yegawasim\\GitHub\\Resume-Builder-app"
    }
  }
}
```

Available tools:

- `fetch_github_profile`: fetches GitHub profile, repositories, README excerpts, and recent commits.
- `fetch_portfolio_content`: fetches the latest portfolio page text and links.
