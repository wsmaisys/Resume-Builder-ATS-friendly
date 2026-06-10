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

## Windows PDF Setup

The app renders resume and cover letter PDFs with WeasyPrint. On Windows, WeasyPrint needs GTK/Pango native libraries in addition to the Python package.

If PDF generation falls back or you see an error like `cannot load library 'libgobject-2.0-0'`, install the native libraries with MSYS2.

1. Install MSYS2 from:

```text
https://www.msys2.org/
```

2. Open `MSYS2 UCRT64` or `MSYS2 MINGW64` from the Start Menu.

3. Update MSYS2:

```bash
pacman -Syu
```

If MSYS2 asks you to close the shell, close it, reopen the same MSYS2 shell, then run:

```bash
pacman -Su
```

4. Install Pango:

```bash
pacman -S mingw-w64-x86_64-pango
```

5. Tell Windows where the DLLs are.

Temporary PowerShell test for the current terminal:

```powershell
$env:WEASYPRINT_DLL_DIRECTORIES="C:\msys64\mingw64\bin"
python -m weasyprint --info
```

Permanent Windows setting:

```powershell
setx WEASYPRINT_DLL_DIRECTORIES "C:\msys64\mingw64\bin"
```

After `setx`, close VS Code and all terminals, then reopen them.

6. Verify WeasyPrint:

```powershell
python -m weasyprint --info
```

You should see a `Pango version` line.

7. Verify PDF generation:

```powershell
python -B -c "from weasyprint import HTML; HTML(string='<h1>Hello</h1>').write_pdf('generated/weasyprint_test.pdf'); print('ok')"
```

If it prints `ok`, the app will use the preferred WeasyPrint HTML/CSS PDF renderer.

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

Recommended tools:

- `candidate_github_repository_catalog`: use before resume/profile refresh tasks that need current GitHub evidence. Returns a structured envelope with profile metadata and compact repo catalog.
- `candidate_github_project_links`: use when an agent needs exact repository URLs, live demo URLs, Docker artifacts, or recent commits for a specific project or keyword.
- `candidate_portfolio_content`: use when an agent needs current visible portfolio text and all normalized links.
- `candidate_portfolio_project_links`: use when an agent needs live demos, GitHub URLs, MCP endpoints, Docker links, publications, or external profile links from the portfolio.

Backward-compatible aliases:

- `fetch_github_profile`
- `fetch_portfolio_content`

All MCP tools are read-only and return the same top-level envelope:

```json
{
  "ok": true,
  "error": null,
  "usage_guidance": "How the LLM should use the returned evidence.",
  "data": {}
}
```

If `ok` is `false`, the caller should read `error.message`, avoid inventing missing facts, and retry only after changing the input or fixing network/authentication.
