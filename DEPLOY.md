
# IntelliPharma - Medical Agent

## Deployment to Vercel

1.  **Database**: The SQLite database (`pharma_agent.db`) is included in the repository for demo purposes.
    *   *Note*: On Vercel, this database will be **read-only** and **ephemeral** (changes won't persist across redeploys). This is fine for referencing the seeded medical data.

2.  **Environment Variables**:
    When importing the project in Vercel, you must add the following **Environment Variables**:
    *   `OPENROUTER_API_KEY`: Your OpenRouter Key (Required for the AI to work).
    *   `OLLAMA_BASE_URL`: (Ignore/Leave empty, we are using OpenRouter).

3.  **Deploy**:
    *   Push the latest code (including the `.db` file).
    *   Go to Vercel -> Add New -> Project -> Import from GitHub.
    *   Select `IntelliPharma`.
    *   Add the `OPENROUTER_API_KEY`.
    *   Click **Deploy**.
