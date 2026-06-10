# AI Resume Builder

A local FastAPI application that generates a tailored resume PDF and cover letter PDF from a pasted job description.

The app uses:

- A cached master candidate profile at `app/data/master_profile.json`
- Mistral for multi-step resume and cover-letter reasoning
- GitHub and portfolio enrichment
- ATS-style evaluation and revision
- HTML/CSS PDF templates rendered by WeasyPrint
- Local MCP servers for current GitHub and portfolio evidence

## What The App Does

1. You paste a job description into the web UI.
2. The app loads the master candidate profile.
3. Optionally, it refreshes current GitHub and portfolio evidence.
4. The JD analyzer extracts must-have skills, nice-to-have skills, responsibilities, ATS keywords, business outcomes, and risk flags.
5. The resume agent runs a multi-call LLM workflow:
   - evidence selection
   - resume draft
   - recruiter/ATS critique
   - final revision
   - deterministic cleanup for unsupported metrics or risky claims
6. The cover-letter agent runs a separate multi-call workflow:
   - application strategy
   - draft
   - critique
   - final revision
7. The ATS evaluator scores the generated resume and returns UI feedback.
8. The PDF service renders both documents.

Generated files follow this convention:

```text
wasim_{company_name}_resume.pdf
wasim_{company_name}_coverletter.pdf
```

Example:

```text
wasim_dizzaract_fz_llc_abu_dhabi_resume.pdf
wasim_dizzaract_fz_llc_abu_dhabi_coverletter.pdf
```

If a file already exists, the app adds `_2`, `_3`, and so on.

## Project Structure

```text
app/
  main.py
  api/
    routes.py
  agents/
    jd_agent.py
    resume_agent.py
    cover_letter_agent.py
    ats_agent.py
    profile_agent.py
  services/
    mistral_service.py
    github_service.py
    portfolio_service.py
    pdf_service.py
    profile_store.py
  mcp_servers/
    github_mcp.py
    portfolio_mcp.py
    contracts.py
  templates/
    resume.html
    cover_letter.html
    index.html
  static/
  data/
    master_profile.json
generated/
requirements.txt
README.md
```

## Install And Run

Run these commands from the project root.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000
```

Health check:

```powershell
Invoke-WebRequest -Uri http://127.0.0.1:8000/health -UseBasicParsing
```

## Environment

Create a `.env` file in the project root.

Required:

```env
MISTRAL_API_KEY=your_mistral_key_here
```

Optional:

```env
MISTRAL_MODEL=mistral-large-latest
GITHUB_TOKEN=github_pat_...
```

The app also accepts the older lowercase key name:

```env
mistral_api_key=...
```

Recommended model:

```env
MISTRAL_MODEL=mistral-large-latest
```

For cheaper local testing, you can use:

```env
MISTRAL_MODEL=mistral-small-latest
```

## GitHub Token

The GitHub token is optional for public data, but recommended because it improves rate limits and allows reliable README/commit fetching.

Create a fine-grained personal access token:

1. Open GitHub.
2. Go to `Settings`.
3. Open `Developer settings`.
4. Open `Personal access tokens`.
5. Choose `Fine-grained tokens`.
6. Click `Generate new token`.
7. Name it, for example `resume-builder-local`.
8. Set an expiration such as 30 or 90 days.
9. Set repository access to public repositories or selected repositories.
10. If GitHub shows repository permissions, choose read-only `Contents`.
11. Generate the token.
12. Add it to `.env`:

```env
GITHUB_TOKEN=github_pat_...
```

Do not commit `.env`. It is ignored by `.gitignore`.

## Windows PDF Setup

The app uses WeasyPrint first because it renders the resume and cover letter from HTML/CSS. On Windows, the Python package also needs native GTK/Pango libraries.

If these native libraries are missing, the app can fall back to ReportLab/plain PDF generation, but the WeasyPrint output is better.

### Step-By-Step MSYS2 Installation

1. Download MSYS2:

   ```text
   https://www.msys2.org/
   ```

2. Run the installer.

3. Use the default install folder if possible:

   ```text
   C:\msys64
   ```

4. Finish installation and open `MSYS2 UCRT64` from the Start Menu.

5. Update package databases and core packages:

   ```bash
   pacman -Syu
   ```

6. If MSYS2 asks you to close the terminal, close it.

7. Reopen `MSYS2 UCRT64`.

8. Finish updates:

   ```bash
   pacman -Su
   ```

9. Install Pango:

   ```bash
   pacman -S mingw-w64-x86_64-pango
   ```

10. Add the DLL directory for WeasyPrint.

    Temporary PowerShell setting for the current terminal:

    ```powershell
    $env:WEASYPRINT_DLL_DIRECTORIES="C:\msys64\mingw64\bin"
    ```

    Permanent Windows setting:

    ```powershell
    setx WEASYPRINT_DLL_DIRECTORIES "C:\msys64\mingw64\bin"
    ```

11. After using `setx`, close VS Code and all terminals, then reopen them.

12. Verify WeasyPrint can see Pango:

    ```powershell
    python -m weasyprint --info
    ```

    You should see a line like:

    ```text
    Pango version: ...
    ```

13. Verify PDF generation:

    ```powershell
    python -B -c "from weasyprint import HTML; HTML(string='<h1>Hello</h1>').write_pdf('generated/weasyprint_test.pdf'); print('ok')"
    ```

If it prints `ok`, WeasyPrint is ready and the app will use the preferred HTML/CSS PDF renderer.

## MCP Servers

This project includes two local MCP stdio servers:

- GitHub MCP server: `app/mcp_servers/github_mcp.py`
- Portfolio MCP server: `app/mcp_servers/portfolio_mcp.py`

Run them manually from the project root:

```powershell
python -m app.mcp_servers.github_mcp
python -m app.mcp_servers.portfolio_mcp
```

### MCP Client Config

Use relative paths when the MCP client is launched from the project root:

```json
{
  "mcpServers": {
    "resume-builder-github": {
      "command": "python",
      "args": ["-m", "app.mcp_servers.github_mcp"],
      "cwd": "."
    },
    "resume-builder-portfolio": {
      "command": "python",
      "args": ["-m", "app.mcp_servers.portfolio_mcp"],
      "cwd": "."
    }
  }
}
```

If your MCP client does not resolve `cwd` relative to this repository, replace `.` with the absolute project path on your machine.

### MCP Tool Contract

All tools are read-only and return the same envelope:

```json
{
  "ok": true,
  "error": null,
  "usage_guidance": "How the LLM should use the returned evidence.",
  "data": {}
}
```

If `ok` is `false`, the LLM should read `error.message`, avoid inventing missing facts, and retry only after changing the input or fixing network/authentication.

### Recommended MCP Tools

- `candidate_github_repository_catalog`: fetches current GitHub evidence, repository metadata, README excerpts, deployment links, artifacts, and recent commits.
- `candidate_github_project_links`: fetches exact repository and deployment links for a project or keyword.
- `candidate_portfolio_content`: fetches the current visible portfolio text and all normalized links.
- `candidate_portfolio_project_links`: groups portfolio links into live demos, GitHub repos, MCP endpoints, Docker artifacts, publications, external profiles, and other links.

Backward-compatible aliases:

- `fetch_github_profile`
- `fetch_portfolio_content`

## App Flow In Code

The main endpoint is:

```text
POST /api/generate
```

Implementation:

```text
app/api/routes.py
```

Flow:

1. `ProfileStore` loads `app/data/master_profile.json`.
2. If `refresh_profile=true`, `ProfileAgent` updates profile evidence from GitHub and portfolio.
3. `JDAnalyzerAgent` extracts role requirements and ATS keywords.
4. `ResumeStrategistAgent` builds the resume through selection, draft, critique, and revision.
5. `ATSEvaluatorAgent` scores the final resume and returns feedback for the UI.
6. `CoverLetterAgent` writes the cover letter through strategy, draft, critique, and revision.
7. `PDFService` renders both PDFs.
8. The API returns:

```json
{
  "match_score": 92,
  "matched_skills": [],
  "missing_skills": [],
  "keywords": [],
  "feedback": [],
  "resume_url": "/download/wasim_company_resume.pdf",
  "cover_letter_url": "/download/wasim_company_coverletter.pdf"
}
```

## Troubleshooting

### Mistral Returns Unauthorized

If you see `401 Unauthorized`, regenerate the Mistral API key and update `.env`.

### WeasyPrint Cannot Load `libgobject`

Install MSYS2/Pango using the Windows PDF setup above, then restart your terminal.

### Generated Resume Looks Generic

Check:

- `MISTRAL_API_KEY` is valid.
- `MISTRAL_MODEL` is not empty.
- The job description is detailed enough.
- `app/data/master_profile.json` has current project evidence.
- The UI was restarted after code changes.

### Files Not Pushed To GitHub

The following are intentionally ignored:

```text
.env
generated/
*.pdf
```

This protects secrets, generated output, and private local documents.
