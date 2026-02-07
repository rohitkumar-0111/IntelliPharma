
# IntelliPharma - Medical Agent

A sovereign, local-first medical intelligence agent powered by Ollama and LangGraph.

## Prerequisites

- Python 3.10+
- [Ollama](https://ollama.com/) (running locally)
- PostgreSQL (Optional, SQLite is used by default)

## Setup

1.  **Clone the repository** (if you haven't already).

2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Setup Environment**:
    - Ensure `.env` exists. Default configuration uses SQLite and local Ollama.
    - `OLLAMA_MODEL=llama3` (Make sure you have pulled this model: `ollama pull llama3`)

4.  **Initialize Database**:
    - The app will automatically create tables on startup.
    - To seed reimbursement data:
        ```bash
        python3 seed_db.py
        ```
    - (Optional) To ingest the full medicine dataset (requires `medicine_dataset.csv` in `data/`):
        ```bash
        python3 scripts/ingest_medicines.py
        ```

## Running the Application

1.  **Start Ollama**:
    Ensure Ollama is running in the background.
    ```bash
    ollama serve
    ```

2.  **Start the Backend & Frontend**:
    ```bash
    uvicorn api.index:app --reload
    ```

3.  **Access the Agent**:
    Open your browser and navigate to:
    [http://127.0.0.1:8000](http://127.0.0.1:8000)

## Features

- **Clinical Intelligence**: RAG over medical guidelines (Mock/Vector DB).
- **Commercial Intelligence**: Compare Government (Ayushman Bharat, CGHS) vs Private (Star Health, etc.) reimbursement schemes.
- **Privacy First**: All inference runs locally.
