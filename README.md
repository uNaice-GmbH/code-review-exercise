# Support Service

Kleiner FastAPI-Service für den Kundensupport.

## Lokal starten

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pytest
uvicorn app.main:app --reload
```

Das LLM ist lokal durch eine feste Antwort ersetzt (`LLM_FAKE=1`), ein API-Key ist nicht nötig.
