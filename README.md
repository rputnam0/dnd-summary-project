# D&D Session Summary Generator

This project automatically generates summaries of D&D sessions using the Google Gemini API.

## Setup

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd dnd-summary-project
    ```

2.  **Create a virtual environment and install dependencies:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    pip install -r requirements.txt
    ```

3.  **Set up your API key:**
    -   Rename the `.env.example` file to `.env`.
    -   Open the `.env` file and add your Google API key:
        ```
        GOOGLE_API_KEY="YOUR_API_KEY"
        ```

## Usage

To generate a summary for a specific session, run the following command:

```bash
python -m src.scripts.run_summary [session_number]
```

For example, to generate a summary for session 32, you would run:

```bash
python -m src.scripts.run_summary 32
```
