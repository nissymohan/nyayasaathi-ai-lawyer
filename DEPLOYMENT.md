# Deploy NyayaSaathi (10-minute self-service steps)

1. Make a new GitHub repository (`nyayasaathi-consumer-help`). Upload the files from this ZIP, not the ZIP itself. Do not upload `.venv/`, private chats, personal IDs, or API credentials.
2. Ensure `app.py`, `engine.py`, `llm_adapter.py`, `requirements.txt` are at the repository root.
3. Visit https://share.streamlit.io/ → New app → select GitHub repo, branch `main`, entrypoint `app.py` → Deploy.
4. If deployment fails, inspect the Streamlit logs. The free default app does not need API keys.
5. Test: standard refund → guided intake → edit and save → generate complaint → download. Test unfamiliar topic and court summons to see refusal.
6. Use the public Streamlit URL and repository/raw_outputs link in the placement form. Check them in an incognito browser.

Optional voice dependency is deliberately NOT installed on Streamlit Cloud by default because of the large model and hosting resource limits.
